# Archived Development Notes

This directory contains historical development notes, bug analyses, and verification reports that have been superseded by consolidated documentation in `docs/`.

## Archived Files

### [gpu-reliance-bug-2025-11.md](gpu-reliance-bug-2025-11.md)
**Original**: `BUG_ANALYSIS_AND_FIX_PLAN.md` (root directory)
**Date**: November 2025
**Topic**: GPU reliance scoring bug in `collect_gpu_data.py`

**Summary**: Comprehensive analysis of logic ordering bug causing GPU-first packages (CuPy, Numba) to be scored as 0 instead of 5. Bug was in lines 178-179 where early return prevented GPU_FIRST_PACKAGES check from executing.

**Status**: Bug fixed
**Current documentation**: `docs/figures/analysis-figures/gpu-reliance.md`

---

### [infrastructure-verification-2025-11-15.md](infrastructure-verification-2025-11-15.md)
**Original**: `analysis/infrastructure-verification-2025-11-15.md`
**Date**: November 15, 2025
**Topic**: Comprehensive LabLink infrastructure verification with evidence

**Summary**: Detailed verification report documenting critical findings:
- PostgreSQL 15 runs inside allocator Docker container (NOT AWS RDS)
- Flask API has 22 endpoints across 5 functional groups
- Client VMs run Python scripts only (NO Flask)
- Complete Terraform resource inventory with evidence

**Status**: Findings incorporated into consolidated documentation
**Current documentation**: `docs/architecture/infrastructure.md`

---

## Purpose of Archive

These files represent important historical development work but are no longer the authoritative source of information. They have been archived for:

1. **Historical record** - Preserving development process and decision-making
2. **Context** - Understanding how current documentation evolved
3. **Bug tracking** - Documenting discovered issues and their fixes
4. **Verification trail** - Evidence of systematic infrastructure analysis

## Current Documentation

For current, authoritative documentation, see:

- **LabLink Architecture**: `docs/architecture/`
- **Figure Generation**: `docs/figures/`
- **Development**: `docs/development/`
- **Main Documentation Index**: `docs/README.md`

## When to Archive

Files should be moved here when:
- They are time-specific reports (dated analysis, verification)
- They are superseded by consolidated documentation
- They are development artifacts (bug analyses, investigation notes)
- They provide historical value but are no longer current reference

## When NOT to Archive

Keep in `analysis/` or other directories when:
- File is work-in-progress research
- File is current authoritative source
- File is actively referenced by other documentation
- File represents ongoing analysis (not yet consolidated)
