"""
Enhanced I Ching Core - Complete data layer with traditional interpretations.
Maintains backward compatibility while improving content quality.

Data source (full Wilhelm–Baynes, all 64 hexagrams):
  Optional: adamblvck/iching-wilhelm-dataset via submodule
  (vendor/iching-wilhelm-dataset/data/iching_wilhelm_translation.js) or
  JSON (data/iching_wilhelm_translation.json or project root). See README.
  When absent, built-in judgment/image/lines for hexagrams 1, 2, 11, 63;
  generic text for the rest. See docs/ADR-002-wilhelm-dataset-extended.md.
"""

import json
import secrets
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class Trigram:
    name: str
    chinese_name: str
    unicode_symbol: str
    element: str
    direction: str
    attribute: str
    family_member: str
    binary: str

@dataclass
class EnhancedHexagram:
    number: int
    chinese_name: str
    english_name: str
    unicode_symbol: str
    binary: str
    upper_trigram: str
    lower_trigram: str
    judgment: str
    image: str
    general_meaning: str
    interpretations: Dict[str, str]  # context-specific interpretations
    changing_lines: Dict[int, str]  # line number -> interpretation
    commentary: Dict[str, str]  # different commentary sources
    # Extended (ADR-002): optional fields from adamblvck/iching-wilhelm-dataset
    pinyin: Optional[str] = None
    hex_unicode: Optional[str] = None
    english_short: Optional[str] = None
    wilhelm_symbolic: Optional[str] = None
    wilhelm_above: Optional[Dict[str, str]] = None
    wilhelm_below: Optional[Dict[str, str]] = None
    judgment_text: Optional[str] = None
    judgment_comments: Optional[str] = None
    image_text: Optional[str] = None
    image_comments: Optional[str] = None
    changing_line_texts: Optional[Dict[int, str]] = None
    changing_line_comments: Optional[Dict[int, str]] = None

class EnhancedIChing:
    """Enhanced I Ching engine with rich traditional content.
    Full Wilhelm–Baynes text (and optional extended fields) when adamblvck
    dataset is present (submodule or data/ JSON); otherwise built-ins only.
    """
    
    def __init__(self):
        self.trigrams = self._load_trigrams()
        self._adamblvck = self._load_wilhelm_dataset_adamblvck()
        self.hexagrams = self._load_hexagrams()
        self.king_wen_sequence = self._build_king_wen_sequence()

    def _load_wilhelm_dataset_adamblvck(self) -> Dict[int, Dict[str, Any]]:
        """Load adamblvck/iching-wilhelm-dataset: submodule .js or local .json.
        Submodule: vendor/iching-wilhelm-dataset (see README). Fallback: data/iching_wilhelm_translation.json
        """
        data_dir = Path(__file__).resolve().parent
        # 1) Submodule: vendor/iching-wilhelm-dataset/data/iching_wilhelm_translation.js
        js_path = data_dir / "vendor" / "iching-wilhelm-dataset" / "data" / "iching_wilhelm_translation.js"
        if js_path.exists():
            try:
                raw = self._parse_adamblvck_js(js_path)
                if raw:
                    return {int(k): v for k, v in raw.items()}
            except (json.JSONDecodeError, OSError):
                pass
        # 2) Local JSON (e.g. committed or downloaded)
        for path in (data_dir / "data" / "iching_wilhelm_translation.json", data_dir / "iching_wilhelm_translation.json"):
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    raw = json.load(f)
                return {int(k): v for k, v in raw.items()}
        return {}

    @staticmethod
    def _parse_adamblvck_js(js_path: Path) -> Dict[str, Any]:
        """Parse adamblvck .js file: 'export default {...};' -> JSON."""
        text = js_path.read_text(encoding="utf-8")
        text = text.strip()
        if text.startswith("export default "):
            text = text[len("export default ") :]
        if text.endswith(";"):
            text = text[:-1]
        return json.loads(text)

    def _adamblvck_hexagram_fields(
        self, num: int, ad: Dict[str, Any], fallback_english: str, fallback_general: str
    ) -> Tuple[str, str, Dict[int, str], str, Dict[str, Any]]:
        """From adamblvck entry return (judgment, image, changing_lines, wilhelm_commentary, extended_kwargs)."""
        j = ad.get("wilhelm_judgment") or {}
        judgment_text = (j.get("text") or "").strip()
        judgment_comments = (j.get("comments") or "").strip()
        judgment = (judgment_text + " " + judgment_comments).strip() or fallback_general
        img = ad.get("wilhelm_image") or {}
        image_text = (img.get("text") or "").strip()
        image_comments = (img.get("comments") or "").strip()
        image = (image_text + " " + image_comments).strip() or f"The image of {fallback_english}."
        lines = ad.get("wilhelm_lines") or {}
        changing_line_texts: Dict[int, str] = {}
        changing_line_comments: Dict[int, str] = {}
        changing_lines: Dict[int, str] = {}
        for n in range(1, 7):
            line = lines.get(str(n)) or {}
            t = (line.get("text") or "").strip()
            c = (line.get("comments") or "").strip()
            changing_line_texts[n] = t
            changing_line_comments[n] = c
            changing_lines[n] = (t + " " + c).strip() or f"Line {n}: Traditional interpretation."
        wilhelm_commentary = judgment_comments or judgment
        extended: Dict[str, Any] = {
            "pinyin": ad.get("pinyin"),
            "hex_unicode": ad.get("hex_font"),
            "english_short": ad.get("english"),
            "wilhelm_symbolic": ad.get("wilhelm_symbolic"),
            "wilhelm_above": ad.get("wilhelm_above"),
            "wilhelm_below": ad.get("wilhelm_below"),
            "judgment_text": judgment_text or None,
            "judgment_comments": judgment_comments or None,
            "image_text": image_text or None,
            "image_comments": image_comments or None,
            "changing_line_texts": changing_line_texts,
            "changing_line_comments": changing_line_comments,
        }
        return judgment, image, changing_lines, wilhelm_commentary, extended

    def _load_trigrams(self) -> Dict[str, Trigram]:
        return {
            "heaven": Trigram("Heaven", "乾", "☰", "Metal", "Northwest", "Creative", "Father", "111"),
            "earth": Trigram("Earth", "坤", "☷", "Earth", "Southwest", "Receptive", "Mother", "000"),
            "thunder": Trigram("Thunder", "震", "☳", "Wood", "East", "Arousing", "Eldest Son", "001"),
            "water": Trigram("Water", "坎", "☵", "Water", "North", "Abysmal", "Middle Son", "010"),
            "mountain": Trigram("Mountain", "艮", "☶", "Earth", "Northeast", "Keeping Still", "Youngest Son", "100"),
            "wind": Trigram("Wind", "巽", "☴", "Wood", "Southeast", "Gentle", "Eldest Daughter", "110"),
            "fire": Trigram("Fire", "離", "☲", "Fire", "South", "Clinging", "Middle Daughter", "101"),
            "lake": Trigram("Lake", "兌", "☱", "Metal", "West", "Joyous", "Youngest Daughter", "011")
        }
    
    def _build_king_wen_sequence(self) -> Dict[str, int]:
        """Build the traditional King Wen sequence mapping binary to hexagram numbers"""
        return {
            "111111": 1, "000000": 2, "010001": 3, "100010": 4, "010111": 5, "111010": 6,
            "000010": 7, "010000": 8, "110111": 9, "111011": 10, "000111": 11, "111000": 12,
            "111101": 13, "101111": 14, "000100": 15, "001000": 16, "011001": 17, "100110": 18,
            "000011": 19, "110000": 20, "101001": 21, "100101": 22, "100000": 23, "000001": 24,
            "111001": 25, "100111": 26, "100001": 27, "011110": 28, "010010": 29, "101101": 30,
            "011100": 31, "001110": 32, "111100": 33, "001111": 34, "101000": 35, "000101": 36,
            "110101": 37, "101011": 38, "010100": 39, "001010": 40, "100011": 41, "110001": 42,
            "011111": 43, "111110": 44, "011000": 45, "000110": 46, "011010": 47, "010110": 48,
            "011101": 49, "101110": 50, "001001": 51, "100100": 52, "110100": 53, "001011": 54,
            "001101": 55, "101100": 56, "110110": 57, "011011": 58, "110010": 59, "010011": 60,
            "110011": 61, "001100": 62, "010101": 63, "101010": 64
        }
    
    def _load_hexagrams(self) -> Dict[int, EnhancedHexagram]:
        """Load enhanced hexagram data with full traditional content"""
        hexagrams = {}
        
        # Enhanced hexagrams with full traditional content
        enhanced_data = {
            1: ("乾", "The Creative", "☰☰", "111111", "heaven", "heaven",
                "The Creative works sublime success, furthering through perseverance.",
                "The movement of heaven is full of power. Thus the superior man makes himself strong and untiring.",
                "Pure yang energy representing initiative, leadership, and creative force. Time for bold action and taking charge of your destiny."),
            2: ("坤", "The Receptive", "☷☷", "000000", "earth", "earth",
                "The Receptive brings about sublime success, furthering through the perseverance of a mare.",
                "The earth's condition is receptive devotion. Thus the superior man who has breadth of character carries the outer world.",
                "Pure yin energy representing receptivity, nurturing, and supportive strength. Time for patience and allowing natural processes to unfold."),
            11: ("泰", "Peace", "☷☰", "000111", "earth", "heaven",
                "The small departs, the great approaches. Good fortune. Success.",
                "Heaven and earth unite: the image of Peace. Thus the ruler divides and completes the course of heaven and earth.",
                "Perfect harmony between heaven and earth, yin and yang. A time of prosperity, understanding, and natural order."),
            63: ("既濟", "After Completion", "☵☲", "010101", "water", "fire",
                "Success in small matters. Perseverance furthers. At the beginning good fortune, at the end disorder.",
                "Water over fire: the image of After Completion. Thus the superior man takes thought of misfortune and arms himself against it in advance.",
                "Goal achieved but vigilance required. Success contains the seeds of its own undoing without continued attention.")
        }
        
        # Standard hexagram data with traditional interpretations
        standard_data = {
            3: ("Difficulty at the Beginning", "010001", "Initial struggles give way to breakthrough. Perseverance through early challenges leads to eventual success."),
            4: ("Youthful Folly", "100010", "Learning through inexperience. Humble acceptance of guidance and willingness to learn bring wisdom."),
            5: ("Waiting", "010111", "Patient anticipation of the right moment. Timing is crucial; premature action leads to failure."),
            6: ("Conflict", "111010", "Inner tension requires resolution. Seek compromise and understanding rather than confrontation."),
            7: ("The Army", "000010", "Disciplined organization achieves goals. Leadership with clear purpose unites diverse elements."),
            8: ("Holding Together", "010000", "Unity through mutual support. Relationships flourish when built on trust and shared values."),
            9: ("Small Accumulation", "110111", "Gentle influence creates change. Small, consistent efforts accumulate into significant transformation."),
            10: ("Treading", "111011", "Careful conduct in delicate situations. Respectful behavior toward authority ensures safe passage."),
            12: ("Standstill", "111000", "Temporary withdrawal preserves strength. Wait for better conditions rather than forcing progress."),
            13: ("Fellowship", "111101", "Unity with like-minded people. Shared purpose and mutual understanding create powerful alliances."),
            14: ("Great Possession", "101111", "Abundance through wisdom and virtue. Great resources carry great responsibility for others' welfare."),
            15: ("Modesty", "000100", "Humble excellence attracts support. True greatness manifests through unpretentious service."),
            16: ("Enthusiasm", "001000", "Inspiring leadership motivates others. Genuine enthusiasm creates momentum for positive change."),
            17: ("Following", "011001", "Adaptability to changing circumstances. Success comes through flexible response to new conditions."),
            18: ("Work on the Decayed", "100110", "Correcting past mistakes brings renewal. Patient restoration of what has deteriorated yields results."),
            19: ("Approach", "000011", "Gradual progress through gentle persistence. Step-by-step advancement builds solid foundations."),
            20: ("Contemplation", "110000", "Reflective observation reveals truth. Understanding comes through careful consideration of patterns."),
            21: ("Biting Through", "101001", "Decisive action overcomes obstacles. Clear judgment followed by firm resolve breaks through barriers."),
            22: ("Grace", "100101", "Beauty enhances substance. Elegant presentation of worthy content attracts positive attention."),
            23: ("Splitting Apart", "100000", "Deterioration requires patient endurance. Protect what matters most while weathering difficult times."),
            24: ("Return", "000001", "Renewal begins from within. Small positive changes initiate cycles of growth and regeneration."),
            25: ("Innocence", "111001", "Natural spontaneity brings good fortune. Authentic action aligned with inner truth succeeds."),
            26: ("Great Accumulation", "100111", "Stored wisdom becomes power. Accumulated knowledge and experience create opportunities for greatness."),
            27: ("Nourishment", "100001", "Careful attention to what feeds growth. Discriminating selection of influences shapes character."),
            28: ("Great Excess", "011110", "Extraordinary times require extraordinary measures. Bold action in crisis situations can transform everything."),
            29: ("The Abysmal Water", "010010", "Danger requires flowing adaptation. Like water, find the path of least resistance through difficulties."),
            30: ("The Clinging Fire", "101101", "Illuminating clarity dispels confusion. Conscious awareness and clear perception guide right action."),
            31: ("Influence", "011100", "Mutual attraction creates connection. Gentle influence and receptive response build lasting relationships."),
            32: ("Duration", "001110", "Enduring stability through consistent principles. Long-term success requires unwavering commitment to values."),
            33: ("Retreat", "111100", "Strategic withdrawal preserves strength. Knowing when to step back prevents unnecessary losses."),
            34: ("Great Power", "001111", "Strength tempered by wisdom. True power lies in restraint and the measured application of force."),
            35: ("Progress", "101000", "Advancing toward enlightenment. Steady forward movement brings recognition and expanded influence."),
            36: ("Darkening of the Light", "000101", "Inner light persists despite outer darkness. Maintain integrity and wisdom during challenging times."),
            37: ("The Family", "110101", "Harmonious relationships create security. Strong foundations at home support success in the world."),
            38: ("Opposition", "101011", "Differences can become complementary. Understanding opposing viewpoints reveals new possibilities."),
            39: ("Obstruction", "010100", "Obstacles offer opportunities for growth. Patience and persistence eventually overcome all barriers."),
            40: ("Deliverance", "001010", "Liberation from restriction brings relief. Quick action after breakthrough prevents return to difficulty."),
            41: ("Decrease", "100011", "Voluntary simplification increases essentials. Reducing excess reveals what truly matters."),
            42: ("Increase", "110001", "Generous sharing multiplies abundance. Helping others succeed creates mutual prosperity."),
            43: ("Breakthrough", "011111", "Determined resolve overcomes final resistance. Clear decision and bold action achieve breakthrough."),
            44: ("Coming to Meet", "111110", "Unexpected encounters bring opportunity. Remain alert to recognise important meetings and messages."),
            45: ("Gathering Together", "011000", "Collective effort amplifies individual power. Unity of purpose creates strength greater than the sum of parts."),
            46: ("Pushing Upward", "000110", "Gradual ascent through persistent effort. Step-by-step advancement builds sustainable success."),
            47: ("Oppression", "011010", "Constraint tests inner strength. Maintaining dignity and purpose during restriction builds character."),
            48: ("The Well", "010110", "Inexhaustible source of wisdom and nourishment. Deep resources serve many when properly accessed."),
            49: ("Revolution", "011101", "Necessary change transforms outdated systems. Revolution succeeds when timing and methods align properly."),
            50: ("The Cauldron", "101110", "Transformation through refinement. Combining diverse elements creates something greater than their sum."),
            51: ("Thunder", "001001", "Shocking awakening brings clarity. Sudden revelations shatter illusions and reveal truth."),
            52: ("Mountain", "100100", "Stillness cultivates inner strength. Meditation and quiet reflection restore balance and wisdom."),
            53: ("Gradual Development", "110100", "Patient progress ensures lasting results. Slow, steady advancement builds unshakeable foundations."),
            54: ("The Marrying Maiden", "001011", "Subordinate position requires careful conduct. Success comes through understanding one's proper role."),
            55: ("Abundance", "001101", "Peak achievement through integrated effort. Maximum potential realized when all elements work in harmony."),
            56: ("The Wanderer", "101100", "Journey brings experience and wisdom. Adaptability and open-mindedness ensure safe passage through foreign territories."),
            57: ("The Gentle Wind", "110110", "Persistent gentle influence creates lasting change. Subtle consistency succeeds where force fails."),
            58: ("The Joyous Lake", "011011", "Cheerful confidence attracts support. Joy shared with others multiplies and returns in abundance."),
            59: ("Dispersion", "110010", "Breaking down barriers enables reunion. Dissolving rigid boundaries allows natural flow to resume."),
            60: ("Limitation", "010011", "Voluntary boundaries create freedom. Self-imposed discipline prevents external limitation."),
            61: ("Inner Truth", "110011", "Sincere understanding creates connection. Authentic communication bridges differences and builds trust."),
            62: ("Small Excess", "001100", "Careful attention to details ensures success. Small, thorough efforts prevent large problems."),
            64: ("Before Completion", "101010", "Final push needed to reach the goal. Careful completion of last steps ensures lasting success.")
        }
        
        # Create enhanced hexagrams for the fully developed ones
        for num, (chinese_name, english_name, unicode_symbol, binary, upper_trigram, lower_trigram, judgment, image, general_meaning) in enhanced_data.items():
            interpretations = {
                "career": f"{general_meaning} Applied to career situations.",
                "relationships": f"{general_meaning} Applied to relationship dynamics.",
                "creative": f"{general_meaning} Applied to creative endeavors.",
                "personal": f"{general_meaning} Applied to personal development.",
                "business": f"{general_meaning} Applied to business decisions."
            }
            ad = self._adamblvck.get(num)
            if ad:
                judgment, image, changing_lines, wilhelm_commentary, extended = self._adamblvck_hexagram_fields(
                    num, ad, english_name, general_meaning
                )
                chinese_name = ad.get("trad_chinese") or chinese_name
                commentary = {
                    "wilhelm": wilhelm_commentary,
                    "psychological": "Traditional commentary on the hexagram's symbolic meaning.",
                    "modern": f"Contemporary application: {general_meaning}"
                }
                hexagrams[num] = EnhancedHexagram(
                    number=num,
                    chinese_name=chinese_name,
                    english_name=english_name,
                    unicode_symbol=unicode_symbol,
                    binary=binary,
                    upper_trigram=upper_trigram,
                    lower_trigram=lower_trigram,
                    judgment=judgment,
                    image=image,
                    general_meaning=general_meaning,
                    interpretations=interpretations,
                    changing_lines=changing_lines,
                    commentary=commentary,
                    **extended
                )
            else:
                # Built-in content when adamblvck (submodule/JSON) not present
                if num == 1:
                    changing_lines = {
                        1: "Hidden dragon. Do not act. The time is not yet right for action. Prepare and cultivate your strength in silence.",
                        2: "Dragon appearing in the field. It furthers one to see the great man. Begin to emerge but seek guidance from experienced mentors.",
                        3: "All day long the superior man is creatively active. At nightfall his mind is still beset with cares. Danger. No blame.",
                        4: "Wavering flight over the depths. No blame. Test your wings cautiously but be prepared to retreat if necessary.",
                        5: "Flying dragon in the heavens. It furthers one to see the great man. Peak of power and influence achieved.",
                        6: "Arrogant dragon will have cause to repent. Overconfidence leads to downfall. Know when to step back."
                    }
                    wilhelm_commentary = "The Creative principle is represented by heaven, which embodies pure yang energy. It symbolizes the power of creation and the drive toward achievement."
                elif num == 2:
                    changing_lines = {
                        1: "When there is hoarfrost underfoot, solid ice is not far off. Pay attention to early warning signs in your situation.",
                        2: "Straight, square, great. Without purpose, yet nothing remains unfurthered. Natural goodness needs no artifice.",
                        3: "Hidden lines. One is able to remain persevering. Work quietly behind the scenes without seeking recognition.",
                        4: "A tied-up sack. No blame, no praise. Sometimes discretion is the better part of valor.",
                        5: "A yellow lower garment brings supreme good fortune. Modesty and appropriateness in all things bring success.",
                        6: "Dragons fight in the meadow. Their blood is black and yellow. When yin energy reaches its extreme, change begins."
                    }
                    wilhelm_commentary = "The Receptive represents the earth principle, pure yin energy that supports and nurtures all life."
                else:
                    changing_lines = {i: f"Line {i}: Traditional changing line interpretation for {english_name}." for i in range(1, 7)}
                    wilhelm_commentary = f"Traditional interpretation: {general_meaning}"
                commentary = {
                    "wilhelm": wilhelm_commentary,
                    "psychological": "Traditional commentary on the hexagram's symbolic meaning.",
                    "modern": f"Contemporary application: {general_meaning}"
                }
                hexagrams[num] = EnhancedHexagram(
                    number=num,
                    chinese_name=chinese_name,
                    english_name=english_name,
                    unicode_symbol=unicode_symbol,
                    binary=binary,
                    upper_trigram=upper_trigram,
                    lower_trigram=lower_trigram,
                    judgment=judgment,
                    image=image,
                    general_meaning=general_meaning,
                    interpretations=interpretations,
                    changing_lines=changing_lines,
                    commentary=commentary
                )
        
        # Create standard hexagrams for the rest
        for num, (english_name, binary, general_meaning) in standard_data.items():
            if num not in hexagrams:
                upper_binary = binary[:3]
                lower_binary = binary[3:]
                upper_trigram = self._binary_to_trigram(upper_binary)
                lower_trigram = self._binary_to_trigram(lower_binary)
                interpretations = {
                    "career": f"{general_meaning} Applied to career matters.",
                    "relationships": f"{general_meaning} Applied to relationship dynamics.",
                    "creative": f"{general_meaning} Applied to creative endeavors.",
                    "personal": f"{general_meaning} Applied to personal growth.",
                    "business": f"{general_meaning} Applied to business decisions."
                }
                ad = self._adamblvck.get(num)
                if ad:
                    judgment, image, changing_lines, wilhelm_commentary, extended = self._adamblvck_hexagram_fields(
                        num, ad, english_name, general_meaning
                    )
                    chinese_name = ad.get("trad_chinese") or f"Hexagram {num}"
                    hexagrams[num] = EnhancedHexagram(
                        number=num,
                        chinese_name=chinese_name,
                        english_name=english_name,
                        unicode_symbol=self._get_unicode_symbol(upper_trigram, lower_trigram),
                        binary=binary,
                        upper_trigram=upper_trigram,
                        lower_trigram=lower_trigram,
                        judgment=judgment,
                        image=image,
                        general_meaning=general_meaning,
                        interpretations=interpretations,
                        changing_lines=changing_lines,
                        commentary={"wilhelm": wilhelm_commentary, "modern": f"Contemporary application: {general_meaning}"},
                        **extended
                    )
                else:
                    # Built-in content when adamblvck (submodule/JSON) not present
                    judgment = general_meaning
                    image = f"The image of {english_name}."
                    changing_lines = {i: f"Line {i}: Traditional interpretation for changing line in {english_name}." for i in range(1, 7)}
                    wilhelm_commentary = f"Traditional interpretation: {general_meaning}"
                    hexagrams[num] = EnhancedHexagram(
                        number=num,
                        chinese_name=f"Hexagram {num}",
                        english_name=english_name,
                        unicode_symbol=self._get_unicode_symbol(upper_trigram, lower_trigram),
                        binary=binary,
                        upper_trigram=upper_trigram,
                        lower_trigram=lower_trigram,
                        judgment=judgment,
                        image=image,
                        general_meaning=general_meaning,
                        interpretations=interpretations,
                        changing_lines=changing_lines,
                        commentary={
                            "wilhelm": wilhelm_commentary,
                            "modern": f"Contemporary application: {general_meaning}"
                        }
                    )
        
        return hexagrams
    
    def _binary_to_trigram(self, binary: str) -> str:
        """Convert binary to trigram name"""
        trigram_map = {
            "111": "heaven", "000": "earth", "001": "thunder", "010": "water",
            "100": "mountain", "110": "wind", "101": "fire", "011": "lake"
        }
        return trigram_map.get(binary, "heaven")
    
    def _get_unicode_symbol(self, upper: str, lower: str) -> str:
        """Get Unicode symbol for hexagram"""
        trigram_symbols = {
            "heaven": "☰", "earth": "☷", "thunder": "☳", "water": "☵",
            "mountain": "☶", "wind": "☴", "fire": "☲", "lake": "☱"
        }
        upper_symbol = trigram_symbols.get(upper, "☰")
        lower_symbol = trigram_symbols.get(lower, "☰")
        return upper_symbol + lower_symbol
    
    def generate_enhanced_divination(self, query: Optional[str] = None) -> Dict[str, Any]:
        """Generate enhanced divination with changing lines"""
        coin_tosses = []
        hexagram_lines = []
        changing_lines = []
        
        # Traditional three-coin method
        for line_pos in range(6):
            tosses = [secrets.choice(['heads', 'tails']) for _ in range(3)]
            coin_tosses.append(tosses)
            
            heads_count = tosses.count('heads')
            
            if heads_count == 3:  # Old Yang - changing yang line
                hexagram_lines.append(1)
                changing_lines.append(line_pos + 1)
            elif heads_count == 2:  # Young Yang - stable yang
                hexagram_lines.append(1)
            elif heads_count == 1:  # Young Yin - stable yin
                hexagram_lines.append(0)
            else:  # heads_count == 0, Old Yin - changing yin line
                hexagram_lines.append(0)
                changing_lines.append(line_pos + 1)
        
        # Calculate hexagram number from binary pattern (bottom to top)
        binary_str = ''.join(str(line) for line in reversed(hexagram_lines))
        hexagram_number = self.king_wen_sequence.get(binary_str, 1)
        
        # Get hexagram data
        hexagram = self.hexagrams.get(hexagram_number)
        
        # Calculate resulting hexagram if there are changing lines
        resulting_hexagram = None
        if changing_lines:
            resulting_binary = list(binary_str)
            for line_num in changing_lines:
                line_index = 6 - line_num  # Convert to 0-based index from bottom
                resulting_binary[line_index] = '0' if resulting_binary[line_index] == '1' else '1'
            
            resulting_number = self.king_wen_sequence.get(''.join(resulting_binary), 1)
            resulting_hexagram = self.hexagrams.get(resulting_number)
        
        return {
            'primary_hexagram': hexagram,
            'changing_lines': changing_lines,
            'resulting_hexagram': resulting_hexagram,
            'coin_tosses': coin_tosses,
            'query': query
        }
    
    def get_contextual_interpretation(self, hexagram_number: int, context: str = "general") -> str:
        """Get context-specific interpretation"""
        hexagram = self.hexagrams.get(hexagram_number)
        if not hexagram:
            return f"Traditional interpretation for hexagram {hexagram_number}"
        
        if context in hexagram.interpretations:
            return hexagram.interpretations[context]
        else:
            return hexagram.general_meaning
    
    def get_changing_line_guidance(self, hexagram_number: int, line_numbers: List[int]) -> List[str]:
        """Get guidance for specific changing lines"""
        hexagram = self.hexagrams.get(hexagram_number)
        if not hexagram:
            return [f"Changing line {line} guidance" for line in line_numbers]
        
        guidance = []
        for line_num in line_numbers:
            if line_num in hexagram.changing_lines:
                guidance.append(f"Line {line_num}: {hexagram.changing_lines[line_num]}")
            else:
                guidance.append(f"Line {line_num}: Traditional changing line interpretation")
        
        return guidance
    
    def infer_context_from_query(self, query: str) -> str:
        """Infer context from query content"""
        if not query:
            return "general"
        
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['work', 'job', 'career', 'promotion', 'boss', 'colleague']):
            return "career"
        elif any(word in query_lower for word in ['relationship', 'love', 'partner', 'marriage', 'dating']):
            return "relationships"
        elif any(word in query_lower for word in ['create', 'art', 'write', 'design', 'music', 'project']):
            return "creative"
        elif any(word in query_lower for word in ['business', 'company', 'startup', 'investment', 'profit']):
            return "business"
        else:
            return "general"

# Backward compatibility adapter
class IChingAdapter:
    """Adapter that provides both simple and enhanced interfaces"""
    
    def __init__(self, use_enhanced: bool = True):
        self.enhanced_engine = EnhancedIChing() if use_enhanced else None
        self.use_enhanced = use_enhanced
    
    def generate_hexagram_by_coins(self) -> Tuple[int, str, str]:
        """Maintain backward compatibility with existing interface"""
        if self.use_enhanced and self.enhanced_engine:
            result = self.enhanced_engine.generate_enhanced_divination()
            hexagram = result['primary_hexagram']
            return hexagram.number, hexagram.english_name, hexagram.general_meaning
        else:
            # Fallback to basic generation
            return self._basic_generation()
    
    def get_hexagram_by_number(self, number: int) -> Tuple[str, str]:
        """Maintain backward compatibility"""
        if self.use_enhanced and self.enhanced_engine:
            hexagram = self.enhanced_engine.hexagrams.get(number)
            if hexagram:
                return hexagram.english_name, hexagram.general_meaning
        
        return f"Hexagram {number}", "Traditional interpretation"
    
    def format_divination_text(self, number: int, name: str, interpretation: str) -> str:
        """Maintain backward compatibility"""
        return f"I Ching Hexagram {number} - {name}: {interpretation}"
    
    def enhanced_consultation(self, query: str) -> Dict[str, Any]:
        """Enhanced consultation method"""
        if self.enhanced_engine:
            return self.enhanced_engine.generate_enhanced_divination(query)
        else:
            return {"error": "Enhanced mode not available"}
    
    def _basic_generation(self) -> Tuple[int, str, str]:
        """Basic fallback generation"""
        number = secrets.randbelow(64) + 1
        return number, f"Hexagram {number}", "Traditional interpretation"

# Global instance for backward compatibility
enhanced_iching = IChingAdapter(use_enhanced=True)
