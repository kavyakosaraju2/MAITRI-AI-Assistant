import 'package:flutter/material.dart';
import 'dart:async';
import 'package:http/http.dart' as http;
import 'dart:convert';

class DashboardScreen extends StatefulWidget {

  final Function(String) onNavigate;

  const DashboardScreen({
    super.key,
    required this.onNavigate
  });

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {

  int emailCount = 0;
  int eventCount = 0;
  int taskCount = 0;

  Future<void> loadDashboard() async {

    final response = await http.get(
      Uri.parse("http://localhost:8000/status")
    );

    final data = jsonDecode(response.body);

    if (!mounted) return;
    
    setState(() {

      emailCount = data["emails"].length;
      eventCount = data["events"].length;
      taskCount = data["tasks"].length;

    });

  }

  @override
  void initState() {
    super.initState();

    loadDashboard();

    Timer.periodic(const Duration(seconds: 30), (timer) {
      loadDashboard();
    });
  }

  Widget dashboardCard(String title, int count, IconData icon, String route) {

    return GestureDetector(

      onTap: () {
        widget.onNavigate(route);
      },

      child: Card(
        elevation: 4,
        margin: const EdgeInsets.all(20),
        child: Container(
          width: 250,
          padding: const EdgeInsets.symmetric(vertical: 30, horizontal: 20),

          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            mainAxisSize: MainAxisSize.min,
            children: [

              Icon(icon, size: 40),

              const SizedBox(height: 10),

              Text(
                "$count",
                style: const TextStyle(
                  fontSize: 36,
                  fontWeight: FontWeight.bold
                ),
              ),

              const SizedBox(height: 5),

              Text(
                title,
                style: const TextStyle(
                  fontSize: 18
                ),
              )

            ],
          ),
        ),
      ),
    );

  }

  @override
  Widget build(BuildContext context) {

    return Center(

      child: Row(

        mainAxisAlignment: MainAxisAlignment.center,
        spacing: 20,

        children: [

          dashboardCard(
            "Emails Today",
            emailCount,
            Icons.email,
            "emails"
          ),

          dashboardCard(
            "Upcoming Events",
            eventCount,
            Icons.calendar_month,
            "calendar"
          ),

          dashboardCard(
            "Pending Tasks",
            taskCount,
            Icons.check_circle,
            "tasks"
          ),

        ],

      ),

    );

  }
}