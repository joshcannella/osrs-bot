package net.runelite.client.plugins.stateexport;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import net.runelite.api.*;
import net.runelite.api.events.*;
import net.runelite.client.eventbus.Subscribe;
import net.runelite.client.plugins.Plugin;
import net.runelite.client.plugins.PluginDescriptor;

import javax.inject.Inject;
import java.io.RandomAccessFile;
import java.nio.ByteOrder;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;

/**
 * State Export — writes game state to a memory-mapped file for cross-process reading.
 *
 * <p>Uses a lock-free sequence counter protocol:
 * <ol>
 *   <li>Increment sequence_before</li>
 *   <li>Write JSON payload</li>
 *   <li>Set sequence_after = sequence_before</li>
 * </ol>
 * Reader checks both counters match to detect torn writes.
 *
 * <p>Buffer layout (64KB):
 * <pre>
 *   [0..3]     sequence_before  (int32 LE)
 *   [4..7]     data_length      (int32 LE)
 *   [8..N]     JSON payload     (UTF-8)
 *   [65532..65535] sequence_after (int32 LE)
 * </pre>
 */
@PluginDescriptor(
    name = "State Export",
    description = "Exports game state to file",
    tags = {"utility"}
)
public class StateExportPlugin extends Plugin
{
    private static final int BUFFER_SIZE = 65536;
    private static final int SEQ_BEFORE_OFFSET = 0;
    private static final int DATA_LEN_OFFSET = 4;
    private static final int DATA_START_OFFSET = 8;
    private static final int SEQ_AFTER_OFFSET = BUFFER_SIZE - 4;

    private static final Gson GSON = new GsonBuilder().create();

    @Inject
    private Client client;

    private RandomAccessFile raf;
    private MappedByteBuffer mmap;
    private int sequence = 0;
    private final GameStateSnapshot snapshot = new GameStateSnapshot();

    @Override
    protected void startUp() throws Exception
    {
        String path = System.getProperty("user.home") + "/.runelite/osrsbot_state.dat";
        raf = new RandomAccessFile(path, "rw");
        raf.setLength(BUFFER_SIZE);
        mmap = raf.getChannel().map(FileChannel.MapMode.READ_WRITE, 0, BUFFER_SIZE);
        mmap.order(ByteOrder.LITTLE_ENDIAN);

        // Zero out buffer to signal "no data yet"
        mmap.putInt(SEQ_BEFORE_OFFSET, 0);
        mmap.putInt(DATA_LEN_OFFSET, 0);
        mmap.putInt(SEQ_AFTER_OFFSET, 0);
    }

    @Override
    protected void shutDown() throws Exception
    {
        if (mmap != null)
        {
            // Zero buffer to signal "plugin stopped" to reader
            mmap.putInt(SEQ_BEFORE_OFFSET, 0);
            mmap.putInt(DATA_LEN_OFFSET, 0);
            mmap.putInt(SEQ_AFTER_OFFSET, 0);
        }
        if (raf != null)
        {
            raf.close();
        }
    }

    // ── Event subscriptions ─────────────────────────────────────────────

    @Subscribe
    public void onGameTick(GameTick event)
    {
        snapshot.updateFromClient(client);
        writeSnapshot();
    }

    @Subscribe
    public void onNpcSpawned(NpcSpawned event)
    {
        snapshot.addNpc(event.getNpc());
    }

    @Subscribe
    public void onNpcDespawned(NpcDespawned event)
    {
        snapshot.removeNpc(event.getNpc());
    }

    @Subscribe
    public void onItemSpawned(ItemSpawned event)
    {
        snapshot.addGroundItem(event.getItem(), event.getTile());
    }

    @Subscribe
    public void onItemDespawned(ItemDespawned event)
    {
        snapshot.removeGroundItem(event.getItem(), event.getTile());
    }

    // ── mmap writer ─────────────────────────────────────────────────────

    // Called only from onGameTick on the RuneLite client thread — not thread-safe
    private void writeSnapshot()
    {
        String json = GSON.toJson(snapshot.toFullState());
        byte[] data = json.getBytes(StandardCharsets.UTF_8);

        if (data.length > BUFFER_SIZE - 12)
        {
            // Payload too large for buffer — skip this tick
            return;
        }

        sequence++;
        mmap.putInt(SEQ_BEFORE_OFFSET, sequence);
        mmap.putInt(DATA_LEN_OFFSET, data.length);
        mmap.position(DATA_START_OFFSET);
        mmap.put(data, 0, data.length);
        mmap.putInt(SEQ_AFTER_OFFSET, sequence);
        // No force() needed — OS page cache handles same-machine coherence
    }
}
