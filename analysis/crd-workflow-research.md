# Chrome Remote Desktop (CRD) Workflow - Research Findings

**Date**: 2025-11-14
**Purpose**: Document actual CRD workflow based on codebase analysis to correct diagram

## Executive Summary

The current CRD connection diagram is **INCORRECT**. It shows an automated workflow where database triggers fire notifications to client VMs, but the actual implementation is **synchronous and blocking** with the client VM actively waiting for user assignment.

## Critical Discovery: Blocking Wait Pattern

### What the Current Diagram Shows (WRONG)
1. User requests VM from allocator
2. Allocator assigns VM → Updates database
3. Database trigger fires → pg_notify()
4. pg_notify() pushes notification to subscribe.py
5. subscribe.py automatically executes CRD command

### What Actually Happens (CORRECT)
1. **User gets CRD code** from Google Chrome Remote Desktop website (https://remotedesktop.google.com/headless)
2. **User submits VM request** via Flask web interface with email + CRD command
3. **Client VM is already waiting** - subscribe.py has been blocking since VM boot
4. **Allocator assigns VM** - Updates database with CRD command
5. **Database trigger fires** - Sends notification via pg_notify()
6. **Waiting subscribe.py receives** the notification and unblocks
7. **subscribe.py executes** connect_crd.py with the CRD command
8. **Chrome Remote Desktop** is configured on the VM
9. **User connects** via Chrome Remote Desktop in browser

## Code Evidence

### 1. User Interface - Where CRD Command is Submitted

**File**: `lablink/packages/allocator/src/lablink_allocator_service/templates/index.html`

```html
<form action="/api/request_vm" method="post">
  <div class="mb-3">
    <label for="email" class="form-label">Email</label>
    <input type="email" id="email" name="email" required />
  </div>
  
  <div class="mb-3">
    <label for="crd_command" class="form-label">CRD Command</label>
    <input type="text" id="crd_command" name="crd_command" 
           placeholder="Enter CRD command" required />
  </div>
  
  <button type="submit">Submit</button>
</form>
```

**Key Points**:
- User must provide BOTH email and CRD command
- Form submits to `/api/request_vm` endpoint
- CRD command is user-provided, not auto-generated

### 2. Allocator API - VM Assignment

**File**: `lablink/packages/allocator/src/lablink_allocator_service/main.py`
**Lines**: 245-288

```python
@app.route("/api/request_vm", methods=["POST"])
def submit_vm_details():
    data = request.form
    email = data.get("email")
    crd_command = data.get("crd_command")
    
    # Validate CRD command
    if not check_crd_input(crd_command=crd_command):
        return render_template("index.html", 
            error="Invalid CRD command received.")
    
    # Check for available VMs
    if len(database.get_unassigned_vms()) == 0:
        return render_template("index.html", 
            error="No available VMs.")
    
    # Assign the VM
    database.assign_vm(email=email, crd_command=crd_command, pin=PIN)
    
    # Display success
    assigned_vm = database.get_vm_details(email=email)
    return render_template("success.html", 
        host=assigned_vm[0], pin=assigned_vm[1])
```

**Key Points**:
- CRD command validation: must contain `--code`
- VM assignment updates database with email, CRD command, and PIN
- Returns success page showing hostname and PIN

### 3. Database Trigger - Notification Mechanism

**File**: `lablink/packages/allocator/src/lablink_allocator_service/generate_init_sql.py`
**Lines**: 51-69

```sql
CREATE OR REPLACE FUNCTION notify_crd_command_update()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify(
        'vm_updates',
        json_build_object(
            'HostName', NEW.HostName,
            'CrdCommand', NEW.CrdCommand,
            'Pin', NEW.Pin
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_crd_command_insert_or_update
AFTER INSERT OR UPDATE OF CrdCommand ON vms
FOR EACH ROW
EXECUTE FUNCTION notify_crd_command_update();
```

**Key Points**:
- Trigger fires on INSERT or UPDATE of `CrdCommand` column
- Sends JSON payload with HostName, CrdCommand, and Pin
- Uses channel name 'vm_updates'

### 4. Database Class - Assign VM Method

**File**: `lablink/packages/allocator/src/lablink_allocator_service/database.py`
**Lines**: 355-383

```python
def assign_vm(self, email, crd_command, pin) -> None:
    """Assign a VM to a user."""
    # Gets the first available VM that is not in use
    hostname = self.get_first_available_vm()
    
    if not hostname:
        raise ValueError("No available VMs to assign.")
    
    # SQL query to update the VM record
    query = f"""
    UPDATE {self.table_name}
    SET useremail = %s, crdcommand = %s, pin = %s, 
        inuse = FALSE, healthy = NULL
    WHERE hostname = %s;
    """
    self.cursor.execute(query, (email, crd_command, pin, hostname))
    self.conn.commit()
```

**Key Points**:
- Updates existing VM row with user email, CRD command, and PIN
- This UPDATE triggers the database trigger
- VM must already exist in database (created during VM provisioning)

### 5. Client VM Startup - The Blocking Wait

**File**: `lablink/packages/client/src/lablink_client_service/subscribe.py`
**Lines**: 24-67

```python
def subscribe(cfg: Config) -> None:
    base_url = os.getenv("ALLOCATOR_URL") or f"http://{cfg.allocator.host}:{cfg.allocator.port}"
    url = f"{base_url}/vm_startup"
    hostname = os.getenv("VM_NAME")
    
    # Retry loop: Keep trying to connect until successful
    retry_count = 0
    retry_delay = 60  # Wait 1 minute between retries
    
    while True:
        try:
            # Send a POST request
            # Note: This endpoint BLOCKS until a user assigns a CRD command,
            # so we use a very long timeout.
            # Timeout tuple: (connect, read) = (30s, 7 days)
            response = requests.post(
                url, json={"hostname": hostname}, 
                timeout=(30, 604800)  # 7 DAYS!
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    command = data["command"]
                    pin = data["pin"]
                    
                    # Execute the command
                    connect_to_crd(pin=pin, command=command)
                    break  # Success - exit retry loop
```

**Key Points**:
- **CRITICAL**: Read timeout is 604,800 seconds (7 DAYS!)
- Client VM POSTs to `/vm_startup` endpoint immediately on boot
- This is a BLOCKING call that waits for a response
- Only exits when it receives CRD command or times out

### 6. Allocator - The Blocking Endpoint

**File**: `lablink/packages/allocator/src/lablink_allocator_service/main.py`
**Lines**: 449-466

```python
@app.route("/vm_startup", methods=["POST"])
def vm_startup():
    data = request.get_json()
    hostname = data.get("hostname")
    
    if not hostname:
        return jsonify({"error": "Hostname is required."}), 400
    
    # Check if the VM exists in the database
    vm = database.get_vm_by_hostname(hostname)
    if not vm:
        return jsonify({"error": "VM not found."}), 404
    
    # THIS IS THE BLOCKING PART
    result = database.listen_for_notifications(
        channel=MESSAGE_CHANNEL, target_hostname=hostname
    )
    
    return jsonify(result), 200
```

**Key Points**:
- Calls `database.listen_for_notifications()` 
- This is a BLOCKING database operation
- Does NOT return until notification received

### 7. Database - The LISTEN/NOTIFY Wait

**File**: `lablink/packages/allocator/src/lablink_allocator_service/database.py`
**Lines**: 182-267

```python
def listen_for_notifications(self, channel, target_hostname) -> dict:
    """Listen for notifications on a specific channel.
    
    Returns:
        dict: A dictionary containing the status, pin, and command.
    """
    # Create a new connection to listen for notifications
    listen_conn = psycopg2.connect(...)
    listen_conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    listen_cursor = listen_conn.cursor()
    
    # Infinite loop to wait for notifications
    try:
        listen_cursor.execute(f"LISTEN {channel};")
        logger.debug(f"Listening for notifications on '{channel}'...")
        
        while True:
            # Wait for notifications (10 second timeout per iteration)
            if select.select([listen_conn], [], [], 10) == ([], [], []):
                continue  # No notification, keep waiting
            else:
                listen_conn.poll()  # Process any pending notifications
                while listen_conn.notifies:
                    notify = listen_conn.notifies.pop(0)
                    payload_data = json.loads(notify.payload)
                    hostname = payload_data.get("HostName")
                    
                    # Check if this notification is for THIS VM
                    if hostname != target_hostname:
                        continue  # Not for us, keep waiting
                    
                    # Got our notification!
                    return {
                        "status": "success",
                        "pin": payload_data.get("Pin"),
                        "command": payload_data.get("CrdCommand"),
                    }
    finally:
        listen_cursor.close()
        listen_conn.close()
```

**Key Points**:
- Uses PostgreSQL `LISTEN` command
- Infinite loop with `select.select()` waiting for notifications
- Only returns when it receives a notification for THIS specific hostname
- This is what blocks the Flask endpoint response

### 8. CRD Command Execution

**File**: `lablink/packages/client/src/lablink_client_service/connect_crd.py`
**Lines**: 96-118

```python
def connect_to_crd(command, pin):
    # Parse the command line arguments
    command = reconstruct_command(command)
    
    # input the pin code with verification
    input_pin = pin + "\n"
    input_pin_verification = input_pin + input_pin
    
    # Execute the command
    result = subprocess.run(
        command,
        input=input_pin_verification,
        shell=True,
        capture_output=True,
        text=True,
    )
```

**Key Points**:
- Reconstructs full CRD command from user-provided code
- Adds PIN twice (for verification)
- Executes via subprocess to configure Chrome Remote Desktop

## Complete Workflow (Actual)

### Phase 1: Infrastructure Setup (Admin)
1. Admin deploys LabLink infrastructure via Terraform
2. Allocator EC2 instance starts with Flask app + PostgreSQL
3. Admin creates client VMs through web UI
4. Client VMs boot and run startup scripts

### Phase 2: Client VM Registration (Automatic on Boot)
1. Client VM starts Docker container
2. Container runs `subscribe.py` as part of startup
3. `subscribe.py` immediately sends POST to `/vm_startup`
4. Allocator receives request, calls `database.listen_for_notifications()`
5. **Client VM is now WAITING** (blocked for up to 7 days)

### Phase 3: User Gets CRD Code (External to LabLink)
1. User navigates to https://remotedesktop.google.com/headless
2. User clicks "Begin" → "Next" → "Authorize"
3. Google provides a command like:
   ```
   DISPLAY= /opt/google/chrome-remote-desktop/start-host \
     --code="4/0AanRJrjkgQ..." \
     --redirect-url="https://remotedesktop.google.com/_/oauthredirect" \
     --name=$(hostname)
   ```
4. User copies this command

### Phase 4: User Requests VM (LabLink Web Interface)
1. User navigates to LabLink allocator web UI (e.g., http://52.10.123.456)
2. User enters:
   - Email address
   - CRD command (paste from Google)
3. User clicks "Submit"

### Phase 5: VM Assignment (Allocator Backend)
1. Flask receives POST to `/api/request_vm`
2. Validates CRD command (must contain `--code`)
3. Checks for available VMs (`database.get_unassigned_vms()`)
4. If available, calls `database.assign_vm(email, crd_command, pin)`
5. Database UPDATE triggers `notify_crd_command_update()` function
6. Trigger calls `pg_notify('vm_updates', JSON payload)`

### Phase 6: Client VM Configuration (Automatic)
1. PostgreSQL sends notification on 'vm_updates' channel
2. `database.listen_for_notifications()` receives notification
3. Validates hostname matches
4. Returns `{status: "success", pin: "123456", command: "..."}`
5. Flask `/vm_startup` endpoint unblocks and returns JSON
6. Client VM `subscribe.py` receives response
7. `subscribe.py` calls `connect_to_crd(pin, command)`
8. `connect_crd.py` executes CRD setup command
9. Chrome Remote Desktop is now configured on VM

### Phase 7: User Accesses VM (Chrome Remote Desktop)
1. User sees success page showing hostname and PIN
2. User navigates to https://remotedesktop.google.com/access/
3. User clicks on the VM (shows up automatically)
4. User enters PIN when prompted
5. User is connected to VM desktop

## Missing Components in Current Diagram

1. **Google Chrome Remote Desktop Website** - Where user gets the code
2. **Flask Web Interface** - Where user submits the code
3. **Blocking wait pattern** - The 7-day timeout on client VM
4. **Success page** - Shows hostname and PIN to user
5. **User accessing remotedesktop.google.com/access** - Final connection step

## Components That Exist But Are Misrepresented

1. **Database trigger** - Exists but diagram makes it look like primary mechanism
2. **subscribe.py** - Not a passive listener, it's actively blocking on HTTP request
3. **pg_notify()** - Not pushing to client VM, it's unblocking a waiting database connection

## API Endpoints Involved

### User-Facing Endpoints (Flask)
- `GET /` - Main page with VM request form
- `POST /api/request_vm` - User submits email + CRD command
- `GET /api/unassigned_vms_count` - Shows available VM count (polling every 5s)

### Client VM Endpoints (Flask)
- `POST /vm_startup` - Client VM blocks waiting for assignment

### Admin Endpoints (Flask, requires auth)
- `GET /admin` - Admin dashboard
- `GET /admin/create` - VM creation interface
- `POST /api/launch` - Create new VMs via Terraform

## Database Schema

**Table**: `vms` (actual name configured, typically `vms` or `vm_table`)

```sql
CREATE TABLE vms (
    HostName VARCHAR(1024) PRIMARY KEY,
    Pin VARCHAR(1024),
    CrdCommand VARCHAR(1024),
    UserEmail VARCHAR(1024),
    InUse BOOLEAN NOT NULL DEFAULT FALSE,
    Healthy VARCHAR(1024),
    Status VARCHAR(1024),
    Logs TEXT,
    TerraformApplyStartTime TIMESTAMP,
    TerraformApplyEndTime TIMESTAMP,
    TerraformApplyDurationSeconds FLOAT,
    CloudInitStartTime TIMESTAMP,
    CloudInitEndTime TIMESTAMP,
    CloudInitDurationSeconds FLOAT,
    ContainerStartTime TIMESTAMP,
    ContainerEndTime TIMESTAMP,
    ContainerStartupDurationSeconds FLOAT,
    TotalStartupDurationSeconds FLOAT,
    CreatedAt TIMESTAMP DEFAULT NOW()
);
```

## Answers to Critical Questions

### 1. Where is the Flask web interface hosted?
**Answer**: On the same EC2 instance as the Allocator, running in a Docker container on port 80 (or 443 with SSL).

### 2. What API endpoint does user call to submit CRD command?
**Answer**: `POST /api/request_vm` with form data `email` and `crd_command`

### 3. How is CRD command stored in database?
**Answer**: Via `UPDATE vms SET crdcommand = %s, useremail = %s, pin = %s WHERE hostname = %s`

### 4. How does client VM know to fetch the CRD command?
**Answer**: It doesn't "know" - it's been waiting since boot. The `/vm_startup` endpoint blocks until the database sends a notification.

### 5. What exactly do subscribe.py and connect_crd.py do?
**Answer**: 
- `subscribe.py`: Makes blocking HTTP POST to allocator's `/vm_startup`, waits for response, then calls `connect_to_crd()`
- `connect_crd.py`: Reconstructs CRD command and executes it via subprocess to configure Chrome Remote Desktop

### 6. Is the Google Chrome Remote Desktop website interaction shown in diagram?
**Answer**: NO - this is completely missing and is a critical first step

## Recommended Diagram Updates

### Components to Add
1. **External Service**: Google Chrome Remote Desktop website (https://remotedesktop.google.com/headless)
2. **User Interface**: Flask Web UI (index.html form)
3. **Final Access**: Chrome Remote Desktop access page (https://remotedesktop.google.com/access)

### Flow to Correct
1. Show user getting code from Google FIRST
2. Show Flask web interface as the entry point for users
3. Show `/vm_startup` endpoint as blocking (not push-based)
4. Clarify that pg_notify unblocks a waiting connection, not pushes to VM
5. Show final user access through Chrome Remote Desktop web interface

### Labels to Update
- Change "Notification (async)" to "Notification (unblocks waiting connection)"
- Change "Execute CRD command" to "Receive response, execute CRD command"
- Add "BLOCKING WAIT" annotation on subscribe.py → allocator connection

## Architecture Pattern Name

This is a **"Long Polling"** or **"Blocking HTTP Request"** pattern, NOT a **"Push Notification"** pattern.

The key insight: Client VMs don't wait for database notifications directly - they wait for HTTP responses that are themselves waiting for database notifications. This adds a layer of indirection that the current diagram completely misses.

## References

- Flask Main: `lablink/packages/allocator/src/lablink_allocator_service/main.py`
- Database: `lablink/packages/allocator/src/lablink_allocator_service/database.py`
- Subscribe: `lablink/packages/client/src/lablink_client_service/subscribe.py`
- Connect CRD: `lablink/packages/client/src/lablink_client_service/connect_crd.py`
- Init SQL: `lablink/packages/allocator/src/lablink_allocator_service/generate_init_sql.py`
- Index Template: `lablink/packages/allocator/src/lablink_allocator_service/templates/index.html`
- Success Template: `lablink/packages/allocator/src/lablink_allocator_service/templates/success.html`
- Architecture Doc: `lablink/docs/architecture.md`
