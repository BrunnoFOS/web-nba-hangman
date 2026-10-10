package io.hangman.nba.controller;

import io.hangman.nba.dto.GameResponse;
import io.hangman.nba.dto.GuessRequest;
import io.hangman.nba.dto.NewGameRequest;
import io.hangman.nba.model.entity.User;
import io.hangman.nba.service.GameService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/api/games")
@RequiredArgsConstructor
public class GameController {

    private final GameService gameService;

    @PostMapping
    public ResponseEntity<GameResponse> startNewGame(
            @AuthenticationPrincipal User user,
            @Valid @RequestBody NewGameRequest request) {
        return ResponseEntity.ok(gameService.createGame(user, request));
    }

    @GetMapping("/{gameId}")
    public ResponseEntity<GameResponse> getGame(
            @AuthenticationPrincipal User user,
            @PathVariable UUID gameId) {
        return ResponseEntity.ok(gameService.getGame(gameId, user));
    }

    @PostMapping("/{gameId}/guess")
    public ResponseEntity<GameResponse> makeGuess(
            @AuthenticationPrincipal User user,
            @PathVariable UUID gameId,
            @Valid @RequestBody GuessRequest request) {
        return ResponseEntity.ok(gameService.processGuess(gameId, user, request.getGuess()));
    }
}
