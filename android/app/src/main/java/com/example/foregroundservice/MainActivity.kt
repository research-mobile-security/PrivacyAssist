package com.example.foregroundservice
import android.content.Context
import android.net.wifi.WifiManager
import android.provider.Settings
import android.util.Log
import com.google.gson.Gson
import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.widget.Button
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val complianceMessage = intent.getStringExtra("compliance_message")
        if (!complianceMessage.isNullOrEmpty()) {
            AlertDialog.Builder(this)
                .setTitle("⚠ Privacy Alert")
                .setMessage(complianceMessage)
                .setPositiveButton("OK", null)
                .show()
        }
        // Find the Button view by its ID from the layout
        val btn = findViewById<Button>(R.id.startServiceButton)
        // Set up an OnClickListener on the button to start the service
        btn.setOnClickListener {
            val intent = Intent(this, MonitorService::class.java)
            //Check for Android version
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                // For Android Oreo or higher
                startForegroundService(intent)
            } else {
                // For older Android versions
                startService(intent)
            }
        }
        }

    }




