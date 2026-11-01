theorem test_p3 (lambda N : Int) : let num := lambda; let den := N * lambda; N * num = den := by intro num den; dsimp [num, den]; rfl
