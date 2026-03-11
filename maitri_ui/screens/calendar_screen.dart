import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class CalendarScreen extends StatefulWidget {
  const CalendarScreen({super.key});

  @override
  State<CalendarScreen> createState() => _CalendarScreenState();
}

class _CalendarScreenState extends State<CalendarScreen> {

  List events = [];

  @override
  void initState() {
    super.initState();
    fetchEvents();
  }

  Future<void> fetchEvents() async {

    final url = Uri.parse("http://127.0.0.1:8000/calendar");

    final response = await http.get(url);

    final data = jsonDecode(response.body);

    setState(() {
      events = data ?? [];
    });

  }

  @override
  Widget build(BuildContext context) {

    if (events.isEmpty) {
      return const Center(child: Text("No events found"));
    }

    return ListView.builder(
      itemCount: events.length,
      itemBuilder: (context, index) {

        final event = events[index];

        String title = "No title";
        String time = "No time";

        if (event is Map) {

          if (event.containsKey("title") && event["title"] != null) {
            title = event["title"].toString();
          }

          if (event.containsKey("time") && event["time"] != null) {

            if (event["time"] is Map) {
              time = event["time"].toString();
            } else {
              time = event["time"].toString();
            }
            }

          }

          return ListTile(
            title: Text(title),
            subtitle: Text(time),
          );
        },
      );
  }
}