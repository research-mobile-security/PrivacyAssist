package com.example.foregroundservice


import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageInfo
import android.content.pm.PackageManager
import android.content.pm.PermissionInfo
import android.net.Uri
import android.net.wifi.WifiManager
import android.os.Build
import android.provider.Settings
import android.util.Log
import com.google.gson.Gson
import okhttp3.Call
import okhttp3.Callback
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response
import java.io.IOException

class InstallReceiver : BroadcastReceiver() {
    // Called when a broadcast message is received ( in this case, when a new app is installed)
    override fun onReceive(context: Context?, intent: Intent?) {
        // Check if the broadcast action is ACTION_PACKAGE_ADDED, which indicates a new app installation
        if (intent?.action == Intent.ACTION_PACKAGE_ADDED) {
            val packageUri: Uri? = intent.data
            // Get the package name ( app ID)
            val packageName = packageUri?.schemeSpecificPart

            // If the installed package is the same as the current app, exit early.
            if(packageName == context?.packageName) return
            Log.d("InstallReceiver", "New App: $packageName")
            // Get the PackageManager to retrieve app-related info.
            val pm= context?.packageManager
            val permission = pm?.getPackageInfo(packageName!!,PackageManager.GET_PERMISSIONS)

            val requestedPermission = permission?.requestedPermissions
            val grantedFlags = permission?.requestedPermissionsFlags
            val permissionsInfo = mutableListOf<String>()
            // If both permissions and flags are available, iterate through them.
            if(requestedPermission !=null && grantedFlags != null){
                for ( i in requestedPermission.indices){
                    val perm = requestedPermission[i]
                    // Check if the corresponding permission was granted.
                    val granted = (grantedFlags[i] and PackageInfo.REQUESTED_PERMISSION_GRANTED) != 0
                    Log.d("InstallReceiver", "Permission: $perm - Granted: $granted")
                    permissionsInfo.add("Permission: $perm - Granted: $granted")

                }
            }
            val androidId = Settings.Secure.getString(context?.contentResolver, Settings.Secure.ANDROID_ID)
            val deviceName = "${Build.MANUFACTURER} ${Build.MODEL}"
            val wifiManager = context?.applicationContext?.getSystemService(Context.WIFI_SERVICE) as WifiManager
            val macAddress = wifiManager.connectionInfo.macAddress ?: "Unavailable"
            val deviceInfo = DeviceInfo(androidId, deviceName, macAddress,packageName.toString(), permissionsInfo)
            val jsonMessage = Gson().toJson(deviceInfo)
            sendToKafka(jsonMessage)
        }

    }
}

private fun sendToKafka(json: String) {
    val client = OkHttpClient()
    val mediaType = "application/json".toMediaType()
    val requestBody = json.toRequestBody(mediaType)

    val request = Request.Builder()
        .url("http://192.168.1.190:5000/send") // ← usa IP della Raspberry
        .post(requestBody)
        .build()

    client.newCall(request).enqueue(object : Callback {
        override fun onFailure(call: Call, e: IOException) {
            Log.e("InstallReceiver", "Errore invio: ${e.message}")
        }

        override fun onResponse(call: Call, response: Response) {
            Log.d("InstallReceiver", "Risposta server: ${response.body?.string()}")
        }
    })
}

