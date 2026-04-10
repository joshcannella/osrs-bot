package scripts.lumbridgecooker;

public enum CookableFood {
    SHRIMPS("Raw shrimps", "Shrimps"),
    ANCHOVIES("Raw anchovies", "Anchovies"),
    SARDINE("Raw sardine", "Sardine"),
    HERRING("Raw herring", "Herring"),
    TROUT("Raw trout", "Trout"),
    SALMON("Raw salmon", "Salmon"),
    TUNA("Raw tuna", "Tuna"),
    LOBSTER("Raw lobster", "Lobster"),
    SWORDFISH("Raw swordfish", "Swordfish"),
    T_BONE_STEAK("Raw t-bone steak", "Cooked t-bone steak");

    private final String rawName;
    private final String cookedName;

    CookableFood(String rawName, String cookedName) {
        this.rawName = rawName;
        this.cookedName = cookedName;
    }

    public String getRawName() { return rawName; }
    public String getCookedName() { return cookedName; }
}
