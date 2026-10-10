package io.hangman.nba.model.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class NbaPlayer {
    private String name;
    private int position; // 1 = Guard, 2 = Forward, 3 = Center
    private String positionName; // "Guard", "Forward", "Center"
    private boolean champ;
    private boolean roy;
    private boolean dpoy;
    private boolean mvp;
    private boolean at75;
    private int difficulty; // 1 = Easy, 2 = Mid, 3 = Hard

    public List<String> getBadges() {
        List<String> badges = new ArrayList<>();
        badges.add(positionName);
        if (champ) badges.add("NBA Champion");
        if (roy) badges.add("ROY");
        if (dpoy) badges.add("DPOY");
        if (mvp) badges.add("MVP");
        if (at75) badges.add("75th TEAM");
        return badges;
    }
}
