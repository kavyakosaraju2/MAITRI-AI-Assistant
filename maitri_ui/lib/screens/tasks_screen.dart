import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class TasksScreen extends StatefulWidget {

  const TasksScreen({super.key});

  @override
  State<TasksScreen> createState() => _TasksScreenState();
}

class _TasksScreenState extends State<TasksScreen> {

  List tasks = [];

  Future<void> loadTasks() async {

    final url = Uri.parse("http://localhost:8000/tasks");

    final response = await http.get(url);

    final data = jsonDecode(response.body);

    if (!mounted) return;
    
    setState(() {
      tasks = data;
    });
  }

  @override
  void initState() {
    super.initState();
    loadTasks();
  }

  @override
  Widget build(BuildContext context) {

    return ListView(
      children: [

        const Padding(
          padding: EdgeInsets.all(20),
          child: Text(
            "Tasks",
            style: TextStyle(fontSize: 24),
          ),
        ),

        for (var task in tasks)

          ListTile(
            leading: const Icon(Icons.check_circle),
            title: Text(task),
          ),

      ],
    );
  }
}