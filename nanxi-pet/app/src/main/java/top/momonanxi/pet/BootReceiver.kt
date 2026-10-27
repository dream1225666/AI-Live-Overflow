package top.momonanxi.pet

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Settings
import androidx.core.content.ContextCompat

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Intent.ACTION_BOOT_COMPLETED) return
        if (!Settings.canDrawOverlays(context)) return
        try {
            ContextCompat.startForegroundService(
                context, Intent(context, PetOverlayService::class.java)
            )
        } catch (_: Throwable) {
        }
    }
}
