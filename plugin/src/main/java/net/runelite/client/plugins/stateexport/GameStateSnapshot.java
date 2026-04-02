package net.runelite.client.plugins.stateexport;

import net.runelite.api.*;
import net.runelite.api.coords.LocalPoint;
import net.runelite.api.coords.WorldPoint;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * Thread-safe snapshot of the current game state.
 *
 * <p>Updated and serialized on the client thread (game tick). Cross-process
 * readers (Python mmap client) use the sequence counter protocol for consistency.
 *
 * <p><b>Coordinate system:</b> All positions exposed as screen canvas coordinates
 * via {@code Perspective.localToCanvas()}, not world tile coordinates.
 * Off-screen entities (where localToCanvas returns null) are omitted.
 */
public class GameStateSnapshot
{
    // ── Player state ────────────────────────────────────────────────────
    private volatile Map<String, Object> player = new ConcurrentHashMap<>();

    // ── NPCs (keyed by NPC index for dedup) ─────────────────────────────
    private final ConcurrentHashMap<Integer, NPC> trackedNpcs = new ConcurrentHashMap<>();

    // ── Inventory ───────────────────────────────────────────────────────
    private volatile List<Map<String, Object>> inventory = new CopyOnWriteArrayList<>();

    // ── Stats ───────────────────────────────────────────────────────────
    private volatile Map<String, Map<String, Object>> stats = new ConcurrentHashMap<>();

    // ── Ground items ────────────────────────────────────────────────────
    private final ConcurrentHashMap<String, Map<String, Object>> groundItems = new ConcurrentHashMap<>();

    // ── Game objects (refreshed every tick) ──────────────────────────────
    private volatile List<Map<String, Object>> objects = new CopyOnWriteArrayList<>();

    // ── Client ref (set on each tick) ───────────────────────────────────
    private volatile Client clientRef;

    // ── Update methods (called from client thread) ──────────────────────

    public void updateFromClient(Client client)
    {
        this.clientRef = client;
        updatePlayer(client);
        updateInventory(client);
        updateStats(client);
        updateObjects(client);
    }

    private void updatePlayer(Client client)
    {
        Player local = client.getLocalPlayer();
        if (local == null) return;

        Map<String, Object> p = new HashMap<>();
        WorldPoint wp = local.getWorldLocation();
        p.put("x", wp.getX());
        p.put("y", wp.getY());
        p.put("plane", wp.getPlane());
        p.put("animation_id", local.getAnimation());

        // HP, prayer, run energy from client
        p.put("hp", client.getBoostedSkillLevel(Skill.HITPOINTS));
        p.put("hp_max", client.getRealSkillLevel(Skill.HITPOINTS));
        p.put("prayer", client.getBoostedSkillLevel(Skill.PRAYER));
        p.put("prayer_max", client.getRealSkillLevel(Skill.PRAYER));
        p.put("run_energy", client.getEnergy() / 100); // RuneLite stores as 0-10000

        // Canvas position of the player
        LocalPoint lp = local.getLocalLocation();
        if (lp != null)
        {
            Point canvasPoint = Perspective.localToCanvas(client, lp, client.getPlane());
            if (canvasPoint != null)
            {
                p.put("canvas_x", canvasPoint.getX());
                p.put("canvas_y", canvasPoint.getY());
            }
        }

        this.player = p;
    }

    private void updateInventory(Client client)
    {
        ItemContainer container = client.getItemContainer(InventoryID.INVENTORY);
        List<Map<String, Object>> inv = new ArrayList<>();

        if (container != null)
        {
            Item[] items = container.getItems();
            for (int i = 0; i < items.length && i < 28; i++)
            {
                Map<String, Object> slot = new HashMap<>();
                slot.put("slot", i);
                slot.put("item_id", items[i].getId());
                slot.put("quantity", items[i].getQuantity());
                inv.add(slot);
            }
        }

        this.inventory = new CopyOnWriteArrayList<>(inv);
    }

    private void updateStats(Client client)
    {
        Map<String, Map<String, Object>> s = new HashMap<>();
        for (Skill skill : Skill.values())
        {
            if (skill == Skill.OVERALL) continue;
            Map<String, Object> entry = new HashMap<>();
            entry.put("level", client.getRealSkillLevel(skill));
            entry.put("boosted", client.getBoostedSkillLevel(skill));
            entry.put("xp", client.getSkillExperience(skill));
            s.put(skill.getName().toLowerCase(), entry);
        }
        this.stats = new ConcurrentHashMap<>(s);
    }

    private void updateObjects(Client client)
    {
        List<Map<String, Object>> objs = new ArrayList<>();
        Scene scene = client.getScene();
        Tile[][][] tiles = scene.getTiles();
        int plane = client.getPlane();

        for (int x = 0; x < Constants.SCENE_SIZE; x++)
        {
            for (int y = 0; y < Constants.SCENE_SIZE; y++)
            {
                Tile tile = tiles[plane][x][y];
                if (tile == null) continue;

                for (GameObject go : tile.getGameObjects())
                {
                    if (go == null) continue;

                    LocalPoint lp = go.getLocalLocation();
                    if (lp == null) continue;

                    Point cp = Perspective.localToCanvas(client, lp, plane);
                    if (cp == null) continue;

                    ObjectComposition def = client.getObjectDefinition(go.getId());

                    Map<String, Object> obj = new HashMap<>();
                    obj.put("id", go.getId());
                    obj.put("name", def != null ? def.getName() : "");
                    obj.put("canvas_x", cp.getX());
                    obj.put("canvas_y", cp.getY());
                    objs.add(obj);
                }
            }
        }

        this.objects = new CopyOnWriteArrayList<>(objs);
    }

    // ── NPC tracking ────────────────────────────────────────────────────

    public void addNpc(NPC npc)
    {
        trackedNpcs.put(npc.getIndex(), npc);
    }

    public void removeNpc(NPC npc)
    {
        trackedNpcs.remove(npc.getIndex());
    }

    // ── Ground item tracking ────────────────────────────────────────────

    public void addGroundItem(TileItem item, Tile tile)
    {
        WorldPoint wp = tile.getWorldLocation();
        String key = item.getId() + "_" + wp.getX() + "_" + wp.getY();
        Map<String, Object> entry = new HashMap<>();
        entry.put("item_id", item.getId());
        entry.put("quantity", item.getQuantity());
        entry.put("world_x", wp.getX());
        entry.put("world_y", wp.getY());
        groundItems.put(key, entry);
    }

    public void removeGroundItem(TileItem item, Tile tile)
    {
        WorldPoint wp = tile.getWorldLocation();
        String key = item.getId() + "_" + wp.getX() + "_" + wp.getY();
        groundItems.remove(key);
    }

    // ── Read methods (called from client thread during serialization) ────

    public Map<String, Object> getPlayer()
    {
        return new HashMap<>(player);
    }

    public List<Map<String, Object>> getInventory()
    {
        return new ArrayList<>(inventory);
    }

    public List<Map<String, Object>> getNpcs()
    {
        Client c = clientRef;
        if (c == null) return Collections.emptyList();

        List<Map<String, Object>> result = new ArrayList<>();
        for (NPC npc : trackedNpcs.values())
        {
            LocalPoint lp = npc.getLocalLocation();
            if (lp == null) continue;

            Point cp = Perspective.localToCanvas(c, lp, c.getPlane());
            if (cp == null) continue; // off-screen, omit

            Map<String, Object> entry = new HashMap<>();
            entry.put("id", npc.getId());
            entry.put("index", npc.getIndex());
            entry.put("name", npc.getName());
            entry.put("canvas_x", cp.getX());
            entry.put("canvas_y", cp.getY());
            entry.put("hp_ratio", npc.getHealthRatio());
            entry.put("animation_id", npc.getAnimation());
            entry.put("is_interacting", npc.getInteracting() != null);
            result.add(entry);
        }
        return result;
    }

    public List<Map<String, Object>> getObjects()
    {
        return new ArrayList<>(objects);
    }

    public Map<String, Map<String, Object>> getStats()
    {
        return new HashMap<>(stats);
    }

    public List<Map<String, Object>> getGroundItems()
    {
        Client c = clientRef;
        if (c == null) return Collections.emptyList();

        List<Map<String, Object>> result = new ArrayList<>();
        for (Map<String, Object> gi : groundItems.values())
        {
            Map<String, Object> entry = new HashMap<>(gi);
            // Try to add canvas coordinates
            int wx = (int) gi.get("world_x");
            int wy = (int) gi.get("world_y");
            LocalPoint lp = LocalPoint.fromWorld(c, wx, wy);
            if (lp != null)
            {
                Point cp = Perspective.localToCanvas(c, lp, c.getPlane());
                if (cp != null)
                {
                    entry.put("canvas_x", cp.getX());
                    entry.put("canvas_y", cp.getY());
                }
            }
            result.add(entry);
        }
        return result;
    }

    public Map<String, Object> toFullState()
    {
        Map<String, Object> state = new HashMap<>();
        state.put("player", getPlayer());
        state.put("inventory", getInventory());
        state.put("npcs", getNpcs());
        state.put("objects", getObjects());
        state.put("stats", getStats());
        state.put("ground_items", getGroundItems());
        return state;
    }
}
