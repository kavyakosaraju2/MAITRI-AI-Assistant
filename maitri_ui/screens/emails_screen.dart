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

  @override
  void initState() {
    super.initState();
    fetchEmails();
  }

  Future<void> fetchEmails() async {

    final url = Uri.parse("http://127.0.0.1:8000/emails");

    final response = await http.get(url);

    final data = jsonDecode(response.body);

    setState(() {
      emails = data;
    });

  }

  @override
  Widget build(BuildContext context) {

    return ListView.builder(
      itemCount: emails.length,
      itemBuilder: (context, index) {

        final email = emails[index];

        return ListTile(
          title: Text(email["subject"] ?? "No subject"),
          subtitle: Text(email["sender"] ?? ""),
        );

      },
    );
  }
}