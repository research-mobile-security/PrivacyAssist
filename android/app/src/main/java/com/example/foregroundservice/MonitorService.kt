package com.example.foregroundservice


import android.app.*
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import org.json.JSONObject

// Define the MonitorService class that extends the Service class
class MonitorService : Service() {

    private lateinit var receiver: InstallReceiver // The receiver to listen for package installations

    override fun onCreate() {
        super.onCreate()
        Log.d("ForegroundService", "Service started")
    }
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        createNotificationChannel()// Create a notification channel for devices
        startForeground(1, buildNotification(), ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC) // Start the service as a foreground service with a notification
        receiver = InstallReceiver()
        // Set up an intent filter to listen for the ACTION_PACKAGE_ADDED broadcast
        val filter = IntentFilter(Intent.ACTION_PACKAGE_ADDED).apply {
            addDataScheme("package")
        }
        // Register the receiver to start listening for the intent
        registerReceiver(receiver, filter)
        // Return START_STICKY so that the service will restart if it's killed by the system
        startComplianceCheckLoop()
        return START_STICKY

    }


    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                "monitor_channel",
                "App Monitor Service",
                NotificationManager.IMPORTANCE_DEFAULT
            )
            // Get the system notification manager to create the channel
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }
    // Function to build the notification to be shown in the foreground service
    private fun buildNotification(): Notification {
        return NotificationCompat.Builder(this, "monitor_channel")
            .setContentTitle("Monitoring started")
            .setContentText("Listening for new installations...")
            .setSmallIcon(android.R.drawable.stat_sys_download_done)
            .build()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        unregisterReceiver(receiver)
    }
    private fun startComplianceCheckLoop() {
        var lastShownMessage: String? = null
        val androidId = android.provider.Settings.Secure.getString(contentResolver, android.provider.Settings.Secure.ANDROID_ID)
        val client = okhttp3.OkHttpClient()
        val url = "http://192.168.1.190:5100/alert-compliance/$androidId"

        Thread {
            while (true) {
                try {
                    val request = okhttp3.Request.Builder()
                        .url(url)
                        .get()
                        .build()

                    val response = client.newCall(request).execute()
                    if (response.isSuccessful) {
                        val body = response.body?.string()
                        if (!body.isNullOrEmpty()&& body != lastShownMessage) {
                            Log.d("ComplianceCheck", "Response body: $body")
                            val json = JSONObject(body)
                            val packageName = json.optString("packageName", "Unknown")
                            val compliance = json.optString("compliance", "Unknown")
                            val reason = json.optString("reason", "No explanation")

                            val formattedMessage = "📦 App: $packageName\n🔐 Status: $compliance\n📝 Reason: $reason"
                            showPopup(formattedMessage)
                            lastShownMessage= body
                        }
                    }
                } catch (e: Exception) {
                    Log.e("ComplianceCheck", "Error: ${e.message}")
                }
                Thread.sleep(10000)  // check every 10 seconds
            }
        }.start()
    }

    private fun showPopup(message: String) {
        val notificationManager = getSystemService(NOTIFICATION_SERVICE) as NotificationManager
        val channelId = "compliance_channel"

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Privacy Compliance",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Privacy alerts from compliance check"
            }
            notificationManager.createNotificationChannel(channel)
        }

        val intent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("compliance_message", message)
        }

        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(this, channelId)
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle("⚠️ Privacy Alert")
            .setContentText("Tap to see details.")
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()

        notificationManager.notify(42, notification)
    }
    }
