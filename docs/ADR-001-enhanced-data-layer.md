# ADR-001: Enhanced I Ching Data Layer Implementation

**Status:** Implemented  
**Date:** 2025-06-10  
**Decision Makers:** Development Team

## Context

The original I Ching server provided simplified interpretations that, while functional, lacked the depth and authenticity expected from a traditional divination system.

## Decision

Implement a modular enhanced data layer that provides rich traditional content while maintaining 100% backward compatibility.

### Architecture Components:

1. **EnhancedIChing Class**: Core engine holding the hexagram data set; each entry records a `content_level` (`full`, `traditional` or `summary`) and `coverage_summary()` reports how much traditional text is authored so far
2. **IChingAdapter**: Compatibility layer maintaining existing interface  
3. **EnhancedBiblioManticDiviner**: Enhanced divination with backward compatibility
4. **Enhanced Server**: Drop-in replacement for existing MCP server

### Backward Compatibility Strategy:

- Adapter pattern preserves all existing method signatures
- Enhanced features are additive, never replacing existing functionality
- Graceful fallback to basic mode if enhanced features unavailable
- Same MCP tool names and parameter structures

## Consequences

### Positive:
- Dramatically improved content quality and authenticity
- Zero breaking changes to production agents
- Rich traditional I Ching experience for new clients
- Gradual migration path allows testing and rollback

### Negative:
- Increased codebase complexity
- Additional maintenance overhead
- Larger memory footprint with full traditional data

## Implementation Notes

- Enhanced hexagrams include full traditional elements
- Changing line calculations use proper three-coin method
- Context inference provides targeted interpretations
- King Wen sequence ensures authentic hexagram mapping

## Amendment — 2026-09-30

The Implementation Notes above describe the intent at decision time. In practice the
traditional texts were authored for only a few hexagrams, and the gap was filled by
deriving judgment, image, contextual and commentary text from each hexagram's summary
sentence. That produced responses which repeated one sentence under several traditional
headings, and filed generated text under the `wilhelm` commentary key.

**Revised decision:** where a traditional text has not been authored, the data layer
leaves the field empty and the formatters omit that section with a note, rather than
substituting derived wording. `content_level` (`full` / `traditional` / `summary`)
records what each entry actually carries, and `coverage_summary()` reports live counts.

This narrows "Enhanced hexagrams include full traditional elements" to the `full` tier.
The trigram system, King Wen mapping and three-coin method remain complete for all 64.
