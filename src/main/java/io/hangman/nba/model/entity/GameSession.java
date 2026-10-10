package io.hangman.nba.model.entity;

import jakarta.persistence.*;
import lombok.*;

import java.util.*;

@Entity
@Table(name = "game_sessions")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class GameSession {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")
    private User user;

    @Column(nullable = false)
    private String targetWord; // Nome do jogador NBA

    private int position;
    private String positionName;
    private boolean champ;
    private boolean roy;
    private boolean dpoy;
    private boolean mvp;
    private boolean at75;
    private int difficulty;

    @Column(nullable = false)
    @Builder.Default
    private int wrongGuesses = 0;

    @Column(nullable = false)
    @Builder.Default
    private int maxTries = 6;

    @ElementCollection(fetch = FetchType.EAGER)
    @CollectionTable(name = "game_used_letters", joinColumns = @JoinColumn(name = "game_id"))
    @Column(name = "letter")
    @Builder.Default
    private Set<Character> usedLetters = new HashSet<>();

    @ElementCollection(fetch = FetchType.EAGER)
    @CollectionTable(name = "game_wrong_letters", joinColumns = @JoinColumn(name = "game_id"))
    @Column(name = "letter")
    @Builder.Default
    private List<Character> wrongLetters = new ArrayList<>();

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    @Builder.Default
    private GameStatus status = GameStatus.IN_PROGRESS;

    public enum GameStatus {
        IN_PROGRESS,
        WIN,
        LOSS
    }
}
