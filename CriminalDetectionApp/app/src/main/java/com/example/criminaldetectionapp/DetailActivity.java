package com.example.criminaldetectionapp;

import android.annotation.SuppressLint;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import com.bumptech.glide.Glide;

public class DetailActivity extends AppCompatActivity {

    ImageView imageView;
    TextView nameText, dateText, timeText;

    @SuppressLint("SetTextI18n")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_detail);

        // Initialize views
        imageView = findViewById(R.id.imageView);
        nameText = findViewById(R.id.nameText);
        dateText = findViewById(R.id.dateText);
        timeText = findViewById(R.id.timeText);

        // Get intent data
        Intent intent = getIntent();
        String name = intent.getStringExtra("name");
        String date = intent.getStringExtra("date");
        String time = intent.getStringExtra("time");
        String imageUrl = intent.getStringExtra("image_url");

        // Set data to views
        nameText.setText("Name: " + name);
        dateText.setText("Date: " + date);
        timeText.setText("Time: " + time);
        Log.d("DetailActivity", "Name: " + name + ", Time: " + time + ", Date: " + date);

        // Load image using Glide
        Glide.with(this)
                .load(imageUrl)
                .placeholder(R.drawable.ic_launcher_background) // fallback image
                .into(imageView);
    }
}
