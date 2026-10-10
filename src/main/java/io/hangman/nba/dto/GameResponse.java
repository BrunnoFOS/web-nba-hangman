package io.hangman.nba.dto;

import io.hangman.nba.model.entity.GameSession.GameStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Set;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class GameResponse {
    private UUID gameId;
    private List<String> badges; // ex: ["Guard", "NBA Champion", "MVP", "75th TEAM"]
    private String maskedWord; // ex: "_ _ _ _ _   _ _ _ _ _ _"
    private List<Character> wrongLetters;
    private Set<Character> usedLetters;
    private int wrongGuesses;
    private int chancesLeft;
    private int maxTries;
    private GameStatus status;
    private String feedbackMessage; // Right guess, wrong guess, already used, etc.
    private String hangmanStageAscii; // Exibe a forca em ASCII como no terminal C++
    private String revealedWord; // Só preenchido se status for WIN ou LOSS
    private Integer userScore; // Pontuação atualizada do usuário se estiver logado
}
