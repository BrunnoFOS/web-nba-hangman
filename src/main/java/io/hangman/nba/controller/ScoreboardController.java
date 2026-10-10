package io.hangman.nba.controller;

import io.hangman.nba.model.entity.User;
import io.hangman.nba.repository.UserRepository;
import lombok.Builder;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/scoreboard")
@RequiredArgsConstructor
public class ScoreboardController {

    private final UserRepository userRepository;

    @Data
    @Builder
    public static class ScoreboardEntry {
        private String username;
        private int score;
        private int gamesWon;
        private int gamesPlayed;
    }

    @GetMapping
    public ResponseEntity<List<ScoreboardEntry>> getLeaderboard() {
        List<User> topUsers = userRepository.findTop10ByOrderByScoreDesc();
        List<ScoreboardEntry> response = topUsers.stream()
                .map(u -> ScoreboardEntry.builder()
                        .username(u.getUsername())
                        .score(u.getScore())
                        .gamesWon(u.getGamesWon())
                        .gamesPlayed(u.getGamesPlayed())
                        .build())
                .collect(Collectors.toList());

        return ResponseEntity.ok(response);
    }
}
