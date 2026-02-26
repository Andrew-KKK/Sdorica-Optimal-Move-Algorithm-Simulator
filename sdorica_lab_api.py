import time
from typing import List, Dict, Optional, Any
from soul_board_simulator import SoulOrbSimulator, OrbColor
from move_algorithm import SdoricaSolver

class SdoricaController:
    """
    Sdorica 實驗控制器 (API)。
    用於執行自動化實驗、收集數據並驗證演算法表現。
    """

    def __init__(self):
        self.sim: Optional[SoulOrbSimulator] = None
        self.solver: Optional[SdoricaSolver] = None
        
        # 實驗設定
        self.priority_list: Dict[str, int] = {}
        
        # 統計數據
        self.turn_count = 0
        self.total_score = 0
        self.one_orb_count = 0   # 紀錄 1 消次數
        self.two_orb_count = 0   # 紀錄 2 消次數
        self.four_orb_count = 0  # 紀錄 4 消次數
        self.history: List[str] = []
        self.is_stuck = False

    def setup_experiment(self, 
                         seed: int, 
                         priority_list: Dict[str, int], 
                         skills: List[str] = None) -> None:
        """
        初始化實驗環境。
        """
        if skills is None:
            skills = ["1-orb", "2-orb", "4-orb-square", "4-orb-L", "4-orb-I", "3-orb-L", "6-orb-rectangle"]
        
        self.sim = SoulOrbSimulator(skills=skills, seed=seed)
        self.solver = SdoricaSolver()
        self.priority_list = priority_list
        
        # 重置統計
        self.turn_count = 0
        self.total_score = 0
        self.one_orb_count = 0
        self.two_orb_count = 0
        self.four_orb_count = 0
        self.history = []
        self.is_stuck = False

    def run_experiment(self, max_turns: int = 100) -> Dict[str, Any]:
        """
        執行自動化實驗，並每 10 次操作顯示一次數據。
        """
        if not self.sim or not self.solver:
            print("請先調用 setup_experiment!")
            return {}

        print(f"--- 開始實驗 (最大回合: {max_turns}) ---")

        for t in range(max_turns):
            self.turn_count = t + 1
            
            # 使用簡化後的優先序演算法尋找最佳移動
            best_move = self.solver.get_best_move_greedy(self.sim, self.priority_list)
            
            if not best_move:
                print(f"第 {t+1} 回合：無法執行任何動作 (卡盤)！")
                self.is_stuck = True
                break
            
            # 更新統計數據
            score = self.solver.get_priority_score(best_move, self.priority_list)
            self.total_score += score
            
            orb_count = best_move['orb_count']
            if orb_count == 1: self.one_orb_count += 1
            elif orb_count == 2: self.two_orb_count += 1
            elif orb_count >= 4: self.four_orb_count += 1
            
            # 執行操作
            self.sim.handle_operation(best_move['coords'])
            self.history.append(best_move['shape'])

            # 每 10 次操作顯示一次數據
            if self.turn_count % 10 == 0:
                self.display_interim_results()

        print(f"--- 實驗結束 (共執行 {self.turn_count} 回合) ---")
        return self.get_summary()

    def display_interim_results(self) -> None:
        """
        顯示階段性的實驗數據。
        """
        avg_score = self.total_score / self.turn_count if self.turn_count > 0 else 0
        print(f"[進度報表] 第 {self.turn_count:>3} 回合 | "
              f"總分: {self.total_score:>5} | "
              f"1消: {self.one_orb_count:>2} | "
              f"2消: {self.two_orb_count:>2} | "
              f"4消+: {self.four_orb_count:>2} | "
              f"平均單回收益: {avg_score:.2f}")

    def get_summary(self) -> Dict[str, Any]:
        """
        獲取最終統計結果。
        """
        return {
            "total_turns": self.turn_count,
            "total_score": self.total_score,
            "one_orb": self.one_orb_count,
            "two_orb": self.two_orb_count,
            "four_orb": self.four_orb_count,
            "avg_score": self.total_score / self.turn_count if self.turn_count > 0 else 0,
            "stuck": self.is_stuck
        }

# --- 實驗指令指令區 ---
if __name__ == "__main__":
    lab = SdoricaController()
    
    # 測試用優先序設定
    test_priority = {
        "1-orb": 10,
        "2-orb": 50,
        "4-orb-square": 200,
    }
    
    # 設定種子碼 42，運行 50 回合
    lab.setup_experiment(seed=42, priority_list=test_priority)
    results = lab.run_experiment(max_turns=50)
    
    print("\n[最終實驗報告]")
    print(f"總分：{results['total_score']}")
    print(f"操作分佈：1消({results['one_orb']}), 2消({results['two_orb']}), 4消+({results['four_orb']})")