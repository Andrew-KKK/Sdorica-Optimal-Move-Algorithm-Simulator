from typing import List, Tuple, Dict, Optional
from soul_board_simulator import SoulOrbSimulator, OrbColor

class SdoricaSolver:
    """
    Sdorica 最佳操作演算法求解器 - 純粹優先序版本 (Pure Priority Version)
    完全依照優先序列表進行決策。
    """
    def __init__(self):
        """
        初始化求解器。
        目前版本為無狀態設計，所有決策參數於呼叫時傳入。
        """
        pass

    def find_all_valid_moves(self, sim: SoulOrbSimulator) -> List[dict]:
        """
        窮舉當前魂盤上所有合法的操作。
        """
        valid_moves = []
        seen_moves = set()

        for r in range(sim.rows):
            for c in range(sim.cols):
                for shape_name, template in sim.SHAPE_TEMPLATES.items():
                    coords = []
                    possible = True
                    
                    for dr, dc in template:
                        nr, nc = r + dr, c + dc
                        if not (0 <= nr < sim.rows and 0 <= nc < sim.cols):
                            possible = False
                            break
                        coords.append((nr, nc))
                    
                    if not possible:
                        continue

                    first_r, first_c = coords[0]
                    base_color = sim.board[first_r][first_c].color
                    
                    if base_color == OrbColor.EMPTY:
                        continue
                        
                    color_match = True
                    for cr, cc in coords[1:]:
                        if sim.board[cr][cc].color != base_color:
                            color_match = False
                            break
                    
                    if not color_match:
                        continue

                    try:
                        # 驗證該形狀是否在當前角色的技能組 (valid_skills) 中
                        validated_shape_name = sim._validate_shape(coords)
                        
                        coords_set = frozenset(coords)
                        if coords_set not in seen_moves:
                            seen_moves.add(coords_set)
                            valid_moves.append({
                                'coords': coords,
                                'shape': validated_shape_name, 
                                'color': base_color,
                                'orb_count': len(coords)
                            })
                            
                    except ValueError:
                        continue
                        
        return valid_moves

    def get_priority_score(self, move: dict, priority_list: Dict[str, int]) -> int:
        """
        僅根據優先序列表計算操作分數。
        """
        shape_name = move['shape']
        
        # 1. 完全匹配 (例如 "4-orb-L_1")
        if shape_name in priority_list:
            return priority_list[shape_name]
        
        # 2. 群組匹配 (例如 "4-orb-L_1" -> "4-orb-L")
        parts = shape_name.rsplit('_', 1)
        group_name = parts[0] if len(parts) > 1 else shape_name
        if group_name in priority_list:
            return priority_list[group_name]
            
        # 3. 萬用型匹配 (例如 "4-orb-any")
        any_group_name = f"{move['orb_count']}-orb-any"
        if any_group_name in priority_list:
            return priority_list[any_group_name]
            
        return 0

    def get_best_move_greedy(self, sim: SoulOrbSimulator, priority_list: Dict[str, int]) -> Optional[dict]:
        """
        [貪婪策略] 找出當前優先序最高的操作。
        """
        all_moves = self.find_all_valid_moves(sim)
        
        if not all_moves:
            return None
            
        best_move = None
        highest_priority = -1 # 確保即使優先序為 0 也能被選中
        
        for move in all_moves:
            score = self.get_priority_score(move, priority_list)
            
            # 若分數相同，保持原順序（或可在此加入次要判斷邏輯，如：優先消除左側魂芯）
            if score > highest_priority:
                highest_priority = score
                best_move = move
            
        return best_move

    def _get_colored_text(self, text: str, color_name: str) -> str:
        """輔助函式：產生帶有顏色的文字"""
        rgb = OrbColor.RGB_MAP.get(color_name, (255, 255, 255))
        r, g, b = rgb
        return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

# --- 測試區 ---
if __name__ == "__main__":
    from soul_board_simulator import SoulOrbSimulator
    
    # 初始化
    skills = ["1-orb", "2-orb", "4-orb-square"]
    sim = SoulOrbSimulator(skills=skills, seed=42)
    
    # 僅設定優先序
    ai_priority = {
        "1-orb": 10,
        "2-orb": 50,
        "4-orb-square": 100
    }
    
    solver = SdoricaSolver()
    sim.display_board()
    
    best = solver.get_best_move_greedy(sim, ai_priority)
    if best:
        print(f"\n=> 決定執行: {best['shape']} (優先序得分: {solver.get_priority_score(best, ai_priority)})")
        sim.handle_operation(best['coords'])
        sim.display_board()