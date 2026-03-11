import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class EmailScreen extends StatefulWidget {

  const EmailScreen({super.key});

  @override
  State<EmailScreen> createState() => _EmailScreenState();
}

class _EmailScreenState extends State<EmailScreen> {

  List emails = [];

  Future<void> loadEmails() async {

    final url = Uri.parse("http://localhost:8000/emails");

    final response = await http.get(url);

    final data = jsonDecode(response.body);

    if (!mounted) return;
    
    setState(() {
      emails = data;
    });
  }

  @override
  void initState() {
    super.initState();
    loadEmails();
  }

  @override
  Widget build(BuildContext context) {

    return ListView(
      children: [

        const Padding(
          padding: EdgeInsets.all(20),
          child: Text(
            "Emails",
            style: TextStyle(fontSize: 24),
          ),
        ),

        for (var email in emails)

          ListTile(
            leading: const Icon(Icons.email),
            title: Text(email["subject"] ?? "No subject"),
            subtitle: Text(email["sender"] ?? ""),
          ),

      ],
    );
  }
}