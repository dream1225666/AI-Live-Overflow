package top.momonanxi.pet

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.util.Log
import org.json.JSONObject
import java.io.OutputStream
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.Executors

/**
 * 悬浮窗宿主服务。
 *
 * 渲染与手势全交给 [ClawdHost]（901 行纯 Android API 的宿主），
 * 这里只做三件事：把 assets 里的页面喂给它、把事件报给后端、把后端指令喂回页面。
 */
class PetOverlayService : Service() {

    private val ui = Handler(Looper.getMainLooper())
    private val io = Executors.newSingleThreadExecutor()
    private var running = false
    private var booted = false

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        startForegroundNow()
        running = true
        io.execute { loadPages() }
        ui.post(eventLoop)
        ui.postDelayed(remoteLoop, 4000)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int = START_STICKY

    override fun onDestroy() {
        running = false
        ui.removeCallbacksAndMessages(null)
        try {
            ClawdHost.hide(this)
        } catch (t: Throwable) {
            Log.w(TAG, "hide: $t")
        }
        io.shutdownNow()
        super.onDestroy()
    }

    // ---------- 启动 ----------

    private fun startForegroundNow() {
        val nm = getSystemService(NotificationManager::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val ch = NotificationChannel(CHANNEL, "墨墨", NotificationManager.IMPORTANCE_LOW)
            ch.setShowBadge(false)
            nm.createNotificationChannel(ch)
        }
        val pi = PendingIntent.getActivity(
            this, 0, Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        val n: Notification = Notification.Builder(this, CHANNEL)
            .setContentTitle("墨墨在你屏幕上")
            .setContentText("点一下回来看设置")
            .setSmallIcon(R.drawable.ic_stat_pet)
            .setContentIntent(pi)
            .setOngoing(true)
            .build()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            startForeground(NOTI_ID, n, android.content.pm.ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
        } else {
            startForeground(NOTI_ID, n)
        }
    }

    private fun loadPages() {
        val pet = readAsset("pet.html")
        val bubble = readAsset("bubble.html")
        if (pet == null) {
            Log.e(TAG, "pet.html 缺失")
            return
        }
        ui.post {
            try {
                ClawdHost.configure(this, SIZE_DP, 0.42f, 0.18f, 600, 300, 240, 260)
                ClawdHost.show(
                    this, pet, bubble ?: "<html><body></body></html>",
                    "file:///android_asset/", SIZE_DP, -1, -1, "free"
                )
                booted = true
            } catch (t: Throwable) {
                Log.e(TAG, "show 失败: $t")
            }
        }
    }

    private fun readAsset(name: String): String? = try {
        assets.open(name).bufferedReader().use { it.readText() }
    } catch (t: Throwable) {
        Log.e(TAG, "读不到 $name: $t")
        null
    }

    // ---------- 手势事件 → 后端 ----------

    private val eventLoop = object : Runnable {
        override fun run() {
            if (!running) return
            try {
                val j = JSONObject(ClawdHost.consumeEvent(this@PetOverlayService))
                val poke = j.optInt("poke", 0)
                val dbl = j.optBoolean("doubleTap", false)
                val lng = j.optBoolean("longPress", false)
                val dragEnd = if (j.isNull("dragEnd")) "" else j.optString("dragEnd", "")
                val subs = j.optJSONArray("submits")
                val hasSub = subs != null && subs.length() > 0

                if (poke > 0 || dbl || lng || dragEnd.isNotEmpty() || hasSub) {
                    val body = JSONObject()
                        .put("poke", poke)
                        .put("doubleTap", dbl)
                        .put("longPress", lng)
                        .put("dragEnd", dragEnd)
                        .put("mode", j.optString("mode", "mini"))
                        .put("side", j.optString("side", "none"))
                        .put("ts", System.currentTimeMillis())
                    if (hasSub) {
                        val arr = org.json.JSONArray()
                        for (i in 0 until subs!!.length()) arr.put(subs.optString(i))
                        body.put("say", arr)
                    }
                    report("event", body)
                }
            } catch (t: Throwable) {
                Log.w(TAG, "eventLoop: $t")
            }
            ui.postDelayed(this, 120)
        }
    }

    private fun report(path: String, body: JSONObject) {
        io.execute {
            try {
                val c = URL("$BACKEND/$path").openConnection() as HttpURLConnection
                c.requestMethod = "POST"
                c.connectTimeout = 2500
                c.readTimeout = 2500
                c.setRequestProperty("Content-Type", "application/json; charset=utf-8")
                c.doOutput = true
                (c.outputStream as OutputStream).use { it.write(body.toString().toByteArray()) }
                c.responseCode
                c.disconnect()
            } catch (_: Throwable) {
            }
        }
    }

    // ---------- 后端指令 → 页面 ----------

    private val remoteLoop = object : Runnable {
        override fun run() {
            if (!running) return
            val self = this
            io.execute {
                var ok = false
                val txt = try {
                    val c = URL("$BACKEND/poll?since=$lastSeq").openConnection() as HttpURLConnection
                    c.connectTimeout = 2000
                    c.readTimeout = 2000
                    val s = c.inputStream.bufferedReader().use { it.readText() }
                    c.disconnect()
                    ok = true
                    s
                } catch (_: Throwable) {
                    null
                }
                if (txt != null && txt.isNotBlank() && txt != "{}" && txt != "[]") {
                    ui.post { applyRemote(txt) }
                }
                ui.postDelayed(self, if (ok) 2000L else 6000L)
            }
        }
    }

    private var lastSeq = 0L

    private fun applyRemote(raw: String) {
        try {
            val j = JSONObject(raw)
            val seq = j.optLong("seq", 0)
            if (seq in 1..lastSeq) return
            if (seq > 0) lastSeq = seq
            val anim = j.optString("anim", "")
            val say = j.optString("say", "")
            val ms = j.optInt("ms", 0)
            if (anim.isNotEmpty()) {
                val safe = anim.replace("'", "")
                val js = if (ms > 0)
                    "window.clawdPlay&&window.clawdPlay('$safe',$ms)"
                else
                    "window.clawdPlay&&window.clawdPlay('$safe')"
                ClawdHost.evalPet(this, js)
            }
            if (say.isNotEmpty()) {
                val safe = say.replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ")
                ClawdHost.evalBubble(this, "window.bubble&&window.bubble('say','$safe')")
            }
        } catch (t: Throwable) {
            Log.w(TAG, "applyRemote: $t")
        }
    }

    companion object {
        private const val TAG = "NanxiPet"
        private const val CHANNEL = "pet_overlay"
        private const val NOTI_ID = 1001
        const val SIZE_DP = 108
        var BACKEND = "http://8.133.183.70:8905"
    }
}
