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

  Future<void> loadEvents() async {

    final url = Uri.parse("http://localhost:8000/calendar");

    final response = await http.get(url);

    final data = jsonDecode(response.body);

    if (!mounted) return;
    
    setState(() {
      events = data;
    });
  }

  @override
  void initState() {
    super.initState();
    loadEvents();
  }

  @override
  Widget build(BuildContext context) {

    return ListView(
      children: [

        const Padding(
          padding: EdgeInsets.all(20),
          child: Text(
            "Calendar Events",
            style: TextStyle(fontSize: 24),
          ),
        ),

        for (var event in events)

          ListTile(
            leading: const Icon(Icons.calendar_month),
            title: Text(event["summary"]),
            subtitle: Text(event["start"]),
          ),

      ],
    );
  }
}