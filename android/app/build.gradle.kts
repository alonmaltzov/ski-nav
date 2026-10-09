plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

// the web app pages (same files the iPhone app bundles), copied in at build time
val webDir = layout.buildDirectory.dir("generated/web")
val copyWeb by tasks.registering(Copy::class) {
    from(rootProject.file("../index.html"), rootProject.file("../nyc.html"))
    from(rootProject.file("../qa/tour.js")) { rename { "qa-tour.js" } }
    into(webDir.map { it.dir("www") })
}

// release signing: CI passes the keystore through env vars; without them the build is debug-signed
val ks = System.getenv("SKINAV_KEYSTORE")

android {
    namespace = "com.alonmaltzov.skinav"
    compileSdk = 35
    defaultConfig {
        applicationId = "com.alonmaltzov.skinav"
        minSdk = 26
        targetSdk = 35
        versionCode = (System.getenv("SKINAV_BUILD") ?: "1").toInt()
        versionName = "1.0." + (System.getenv("SKINAV_BUILD") ?: "1")
    }
    signingConfigs {
        if (ks != null) create("release") {
            storeFile = file(ks)
            storePassword = System.getenv("SKINAV_KEYSTORE_PASSWORD")
            keyAlias = "skinav"
            keyPassword = System.getenv("SKINAV_KEYSTORE_PASSWORD")
        }
    }
    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = if (ks != null) signingConfigs.getByName("release") else signingConfigs.getByName("debug")
        }
    }
    sourceSets["main"].assets.srcDir(webDir)
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}

tasks.named("preBuild") { dependsOn(copyWeb) }

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.activity:activity-ktx:1.9.3")
    implementation("com.google.android.gms:play-services-location:21.3.0")
    implementation("androidx.fragment:fragment-ktx:1.8.5")   // play-services pulls an old fragment; permission results need 1.3+
}
