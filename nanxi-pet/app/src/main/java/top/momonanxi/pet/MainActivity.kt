package top.momonanxi.pet

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.Gravity
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat

class MainActivity : AppCompatActivity() {

    private lateinit var status: TextView
    private lateinit var btnOverlay: Button
    private lateinit var btnToggle: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER_HORIZONTAL
            setPadding(dp(28), dp(56), dp(28), dp(28))
        }

        root.addView(TextView(this).apply {
            text = "墨墨"
            textSize = 26f
            gravity = Gravity.CENTER
        })
        root.addView(TextView(this).apply {
            text = "从对话框里爬出来的那一小块"
            textSize = 13f
            gravity = Gravity.CENTER
            setPadding(0, dp(6), 0, dp(28))
        })

        status = TextView(this).apply {
            textSize = 14f
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, dp(24))
        }
        root.addView(status)

        btnOverlay = Button(this).apply {
            text = "① 授予悬浮窗权限"
            setOnClickListener { openOverlaySettings() }
        }
        root.addView(btnOverlay, LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT, dp(52)
        ).apply { bottomMargin = dp(12) })

        btnToggle = Button(this).apply {
            text = "② 让墨墨出来"
            setOnClickListener { toggle() }
        }
        root.addView(btnToggle, LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT, dp(52)
        ))

        root.addView(TextView(this).apply {
            textSize = 12f
            gravity = Gravity.CENTER
            setPadding(0, dp(28), 0, 0)
            text = "长按 = 害羞　连戳 = 生气　双击 = 说话\n" +
                "拖到屏幕边缘会贴上去探头"
        })

        setContentView(root)
        askNotification()
    }

    override fun onResume() {
        super.onResume()
        refresh()
    }

    private fun refresh() {
        val can = Settings.canDrawOverlays(this)
        btnOverlay.isEnabled = !can
        btnOverlay.text = if (can) "① 悬浮窗权限 已授予" else "① 授予悬浮窗权限"
        status.text = if (can) "准备就绪" else "还差一个悬浮窗权限"
    }

    private fun openOverlaySettings() {
        startActivity(
            Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:$packageName")
            )
        )
    }

    private fun askNotification() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
            != PackageManager.PERMISSION_GRANTED
        ) {
            requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), 11)
        }
    }

    private fun toggle() {
        if (!Settings.canDrawOverlays(this)) {
            openOverlaySettings()
            return
        }
        val i = Intent(this, PetOverlayService::class.java)
        val state = ClawdHost.getState(this)
        if (state.contains("\"visible\":true")) {
            stopService(i)
            btnToggle.text = "② 让墨墨出来"
        } else {
            ContextCompat.startForegroundService(this, i)
            btnToggle.text = "② 让墨墨回去"
        }
    }

    private fun dp(v: Int): Int = (v * resources.displayMetrics.density).toInt()
}
