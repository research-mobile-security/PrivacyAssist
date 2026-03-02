package com.example.foregroundservice

data class DeviceInfo(
    val androidId: String,
    val deviceName: String,
    val macAddress: String,
    val packageName: String,
    val grantedPermissions: List<String>
)
