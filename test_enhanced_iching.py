#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced I Ching System
Validates backward compatibility and enhanced features
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from bibliomantic_server.enhanced_iching_core import IChingAdapter, EnhancedIChing
    from bibliomantic_server.enhanced_divination import EnhancedBiblioManticDiviner
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False

# Always test original implementation
from bibliomantic_server.iching import IChing
from bibliomantic_server.divination import BiblioManticDiviner

class TestBackwardCompatibility:
    """Ensure zero breaking changes to existing functionality"""
    
    def test_original_iching_interface(self):
        """Test original IChing interface unchanged"""
        iching = IChing()
        
        # Test coin generation
        number, name, interpretation = iching.generate_hexagram_by_coins()
        assert isinstance(number, int)
        assert 1 <= number <= 64
        assert isinstance(name, str)
        assert len(name) > 0
        assert isinstance(interpretation, str)
        assert len(interpretation) > 10
        
        # Test hexagram lookup
        lookup_name, lookup_interp = iching.get_hexagram_by_number(1)
        assert lookup_name == "The Creative"
        assert "creative force" in lookup_interp.lower()
        
        # Test formatting
        formatted = iching.format_divination_text(1, "The Creative", "Test interpretation")
        assert "I Ching Hexagram 1 - The Creative: Test interpretation" == formatted
    
    def test_original_diviner_interface(self):
        """Test original BiblioManticDiviner interface unchanged"""
        diviner = BiblioManticDiviner()
        
        # Test simple divination
        result = diviner.perform_simple_divination()
        assert result["success"] is True
        assert "hexagram_number" in result
        assert "hexagram_name" in result
        assert "interpretation" in result
        assert "formatted_text" in result
        
        # Test query augmentation
        query = "Test query"
        augmented, info = diviner.divine_query_augmentation(query)
        assert query in augmented
        assert "hexagram_number" in info
        assert "hexagram_name" in info
        assert "interpretation" in info
        
        # Test statistics
        stats = diviner.get_divination_statistics()
        assert stats["total_hexagrams"] == 64
        assert stats["system_status"] == "operational"

@pytest.mark.skipif(not ENHANCED_AVAILABLE, reason="Enhanced features not available")
class TestEnhancedFeatures:
    """Test enhanced functionality"""
    
    def test_enhanced_iching_creation(self):
        """Test enhanced IChing engine creation"""
        enhanced = EnhancedIChing()
        assert len(enhanced.hexagrams) == 64
        assert len(enhanced.trigrams) == 8
        assert len(enhanced.king_wen_sequence) == 64
    
    def test_enhanced_hexagram_quality(self):
        """Test enhanced hexagram content quality"""
        enhanced = EnhancedIChing()
        
        # Test hexagram 1 (fully enhanced)
        hex1 = enhanced.hexagrams[1]
        assert hex1.chinese_name == "乾"
        assert hex1.english_name == "The Creative"
        assert hex1.unicode_symbol == "☰☰"
        assert "perseverance" in hex1.judgment.lower()
        assert "heaven" in hex1.image.lower()
        assert len(hex1.interpretations) >= 5
        assert len(hex1.changing_lines) == 6
        assert len(hex1.commentary) >= 2
    
    def test_adapter_backward_compatibility(self):
        """Test adapter maintains exact interface"""
        adapter = IChingAdapter(use_enhanced=True)
        
        # Test original methods work
        number, name, interpretation = adapter.generate_hexagram_by_coins()
        assert isinstance(number, int)
        assert 1 <= number <= 64
        assert isinstance(name, str)
        assert isinstance(interpretation, str)
        
        # Test lookup
        lookup_name, lookup_interp = adapter.get_hexagram_by_number(1)
        assert isinstance(lookup_name, str)
        assert isinstance(lookup_interp, str)
        
        # Test formatting
        formatted = adapter.format_divination_text(1, "Test", "Test interp")
        assert "I Ching Hexagram 1 - Test: Test interp" == formatted
    
    def test_enhanced_diviner_compatibility(self):
        """Test enhanced diviner maintains compatibility"""
        diviner = EnhancedBiblioManticDiviner(use_enhanced=True)
        
        # Test original interface
        result = diviner.perform_simple_divination()
        assert result["success"] is True
        assert "hexagram_number" in result
        assert "hexagram_name" in result
        assert "interpretation" in result
        
        # Test enhanced features
        if result.get("enhanced"):
            assert "changing_lines" in result

class TestPerformance:
    """Test performance requirements"""
    
    def test_divination_speed(self):
        """Test divination performance"""
        import time
        
        # Test original performance
        diviner = BiblioManticDiviner()
        start = time.time()
        for _ in range(10):
            diviner.perform_simple_divination()
        original_time = time.time() - start
        
        # Test enhanced performance (if available)
        if ENHANCED_AVAILABLE:
            enhanced_diviner = EnhancedBiblioManticDiviner(use_enhanced=True)
            start = time.time()
            for _ in range(10):
                enhanced_diviner.perform_simple_divination()
            enhanced_time = time.time() - start
            
            # Enhanced should not be more than 2x slower
            assert enhanced_time < original_time * 2
        
        # Both should complete quickly
        assert original_time < 1.0

@pytest.mark.skipif(not ENHANCED_AVAILABLE, reason="Enhanced features not available")
class TestContentCoverage:
    """The data set must describe itself truthfully and render line guidance cleanly"""

    def test_changing_line_guidance_has_single_prefix(self):
        """Regression: placeholder line texts once began with 'Line N:', giving 'Line N: Line N: ...'"""
        import re
        engine = EnhancedIChing()
        for number in range(1, 65):
            for guidance in engine.get_changing_line_guidance(number, [1, 2, 3, 4, 5, 6]):
                assert re.fullmatch(r"Line [1-6]: (?!Line \d).+", guidance), f"hexagram {number}: {guidance!r}"

    def test_coverage_summary_matches_data(self):
        """content_level must agree with what each hexagram actually carries"""
        engine = EnhancedIChing()
        coverage = engine.coverage_summary()
        assert coverage["total"] == 64
        assert coverage["full"] + coverage["traditional"] + coverage["summary"] == 64
        assert coverage["full"] >= 1  # at least hexagram 1 is fully authored
        for hexagram in engine.hexagrams.values():
            traditional_tier = hexagram.content_level in ("full", "traditional")
            # Chinese name, judgment and image exist exactly for the traditional tiers
            assert bool(hexagram.chinese_name) == traditional_tier, hexagram.number
            assert bool(hexagram.judgment) == traditional_tier, hexagram.number
            assert bool(hexagram.image) == traditional_tier, hexagram.number
            # Changing-line, contextual and commentary texts exist only where fully authored
            fully_authored = hexagram.content_level == "full"
            assert bool(hexagram.changing_lines) == fully_authored, hexagram.number
            assert bool(hexagram.commentary) == fully_authored, hexagram.number
            assert bool(hexagram.interpretations) == fully_authored, hexagram.number

    def test_no_generated_text_presented_as_traditional(self):
        """Nothing may be synthesized from general_meaning and served as traditional text"""
        engine = EnhancedIChing()
        for hexagram in engine.hexagrams.values():
            summary = hexagram.general_meaning
            for field in (hexagram.judgment, hexagram.image):
                assert summary not in (field or ""), hexagram.number
            for text in list(hexagram.commentary.values()) + list(hexagram.interpretations.values()):
                assert summary not in text, hexagram.number
            for text in hexagram.changing_lines.values():
                assert "not yet included" not in text, hexagram.number

    def test_statistics_report_coverage(self):
        """Server statistics must carry the live coverage counts, not a hardcoded claim"""
        stats = EnhancedBiblioManticDiviner(use_enhanced=True).get_divination_statistics()
        assert stats["content_coverage"] == EnhancedIChing().coverage_summary()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
