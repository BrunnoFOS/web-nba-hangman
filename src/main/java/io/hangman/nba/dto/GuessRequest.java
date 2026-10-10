package io.hangman.nba.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GuessRequest {
    @NotBlank(message = "Guess cannot be empty")
    private String guess;
}
