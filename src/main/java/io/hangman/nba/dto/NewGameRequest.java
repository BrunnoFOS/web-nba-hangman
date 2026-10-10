package io.hangman.nba.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class NewGameRequest {
    /**
     * Dificuldade (1 = Easy, 2 = Mid, 3 = Hard)
     */
    @Min(1)
    @Max(3)
    private int difficulty;

    /**
     * Categoria:
     * 1 = CHAMP
     * 2 = Guard
     * 3 = Forward
     * 4 = Center
     * 5 = ROY
     * 6 = DPOY
     * 7 = MVP
     * 8 = 75AT
     */
    @Min(1)
    @Max(8)
    private int category;
}
