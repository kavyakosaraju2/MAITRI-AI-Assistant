import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class DashboardScreen extends StatefulWidget {

  final Function(String) onNavigate;

  const DashboardScreen({super.key, required this.onNavigate});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {

  Map data = {};

  @override
  void initState() {
    super.initState();
    fetchDashboard();
  }

  Future<void> fetchDashboard() async {

    final url = Uri.parse("http://127.0.0.1:8000/dashboard");

    final response = await http.get(url);

    final result = jsonDecode(response.body);

    setState(() {
      data = result;
    });

  }

  @override
  Widget build(BuildContext context) {

    return Column(
      children: [

        ListTile(
          title: Text("Emails: ${data["emails"] ?? 0}"),
          onTap: () => widget.onNavigate("emails"),
        ),

        ListTile(
          title: Text("Tasks: ${data["tasks"] ?? 0}"),
          onTap: () => widget.onNavigate("tasks"),
        ),

        ListTile(
          title: Text("Meetings: ${data["events"] ?? 0}"),
          onTap: () => widget.onNavigate("calendar"),
        ),

      ],
    );
  }
}