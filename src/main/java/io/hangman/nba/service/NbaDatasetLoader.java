package io.hangman.nba.service;

import io.hangman.nba.model.entity.NbaPlayer;
import jakarta.annotation.PostConstruct;
import lombok.Getter;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

@Service
public class NbaDatasetLoader {

    @Getter
    private final List<NbaPlayer> allPlayers = new ArrayList<>();
    @Getter
    private final List<NbaPlayer> easyPlayers = new ArrayList<>();
    @Getter
    private final List<NbaPlayer> midPlayers = new ArrayList<>();
    @Getter
    private final List<NbaPlayer> hardPlayers = new ArrayList<>();

    @PostConstruct
    public void loadCsv() {
        try {
            ClassPathResource resource = new ClassPathResource("nba-database.csv");
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(resource.getInputStream(), StandardCharsets.UTF_8))) {
                String line = reader.readLine(); // Header: Name,Position,CHAMP,ROY,DPOY,MVP,75AT,Difficulty

                while ((line = reader.readLine()) != null) {
                    if (line.isBlank()) continue;
                    String[] tokens = line.split(",");
                    if (tokens.length < 8) continue;

                    String name = tokens[0].trim().toUpperCase();
                    String posStr = tokens[1].trim();
                    int position;
                    if (posStr.equalsIgnoreCase("Guard")) {
                        position = 1;
                    } else if (posStr.equalsIgnoreCase("Forward")) {
                        position = 2;
                    } else {
                        position = 3; // Center
                    }

                    boolean champ = tokens[2].trim().equalsIgnoreCase("YES");
                    boolean roy = tokens[3].trim().equalsIgnoreCase("YES");
                    boolean dpoy = tokens[4].trim().equalsIgnoreCase("YES");
                    boolean mvp = tokens[5].trim().equalsIgnoreCase("YES");
                    boolean at75 = tokens[6].trim().equalsIgnoreCase("YES");
                    int difficulty = Integer.parseInt(tokens[7].trim());

                    NbaPlayer player = NbaPlayer.builder()
                            .name(name)
                            .position(position)
                            .positionName(posStr)
                            .champ(champ)
                            .roy(roy)
                            .dpoy(dpoy)
                            .mvp(mvp)
                            .at75(at75)
                            .difficulty(difficulty)
                            .build();

                    allPlayers.add(player);
                    if (difficulty == 3) {
                        hardPlayers.add(player);
                    } else if (difficulty == 2) {
                        midPlayers.add(player);
                    } else {
                        easyPlayers.add(player);
                    }
                }
            }
        } catch (Exception e) {
            throw new RuntimeException("Failed to load NBA database CSV", e);
        }
    }

    public List<NbaPlayer> filterPlayers(int difficulty, int category) {
        List<NbaPlayer> sourceList;
        if (difficulty == 1) {
            sourceList = easyPlayers;
        } else if (difficulty == 2) {
            sourceList = midPlayers;
        } else {
            sourceList = hardPlayers;
        }

        List<NbaPlayer> filtered = new ArrayList<>();
        for (NbaPlayer player : sourceList) {
            boolean match = switch (category) {
                case 1 -> player.isChamp();
                case 2 -> player.getPosition() == 1; // Guard
                case 3 -> player.getPosition() == 2; // Forward
                case 4 -> player.getPosition() == 3; // Center
                case 5 -> player.isRoy();
                case 6 -> player.isDpoy();
                case 7 -> player.isMvp();
                case 8 -> player.isAt75();
                default -> false;
            };

            if (match) {
                filtered.add(player);
            }
        }
        return filtered;
    }
}
