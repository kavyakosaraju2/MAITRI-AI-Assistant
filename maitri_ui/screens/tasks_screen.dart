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

  @override
  void initState() {
    super.initState();
    fetchTasks();
  }

  Future<void> fetchTasks() async {

    final url = Uri.parse("http://127.0.0.1:8000/tasks");

    final response = await http.get(url);

    final data = jsonDecode(response.body);

    setState(() {
      tasks = data ?? [];
    });

  }

  @override
  Widget build(BuildContext context) {

    if (tasks.isEmpty) {
      return const Center(child: Text("No tasks found"));
    }

    return ListView.builder(
      itemCount: tasks.length,
      itemBuilder: (context, index) {

        final task = tasks[index];

        String title = "Untitled task";

        if (task is Map) {
          if (task.containsKey("title") && task["title"] != null) {
            title = task["title"].toString();
          }
        }

        return ListTile(
          title: Text(title),
        );
      },
    );
  }
}