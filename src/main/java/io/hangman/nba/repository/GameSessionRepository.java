package io.hangman.nba.repository;

import io.hangman.nba.model.entity.GameSession;
import io.hangman.nba.model.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface GameSessionRepository extends JpaRepository<GameSession, UUID> {
    List<GameSession> findByUser(User user);
}
