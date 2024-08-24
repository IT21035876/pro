import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: ImagePickerApp(),
    );
  }
}

class ImagePickerApp extends StatefulWidget {
  @override
  _ImagePickerAppState createState() => _ImagePickerAppState();
}

class _ImagePickerAppState extends State<ImagePickerApp> {
  File? _image;
  final picker = ImagePicker();
  String _prediction = '';

  Future getImage() async {
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);

    setState(() {
      if (pickedFile != null) {
        _image = File(pickedFile.path);
      } else {
        print('No image selected.');
      }
    });
  }

  Future uploadImage(File image) async {
    final uri = Uri.parse('http://127.0.0.1:5001/predict');
    var request = http.MultipartRequest('POST', uri)
      ..files.add(await http.MultipartFile.fromPath('image', image.path));
    
    var response = await request.send();

    if (response.statusCode == 200) {
      var responseData = await http.Response.fromStream(response);
      var jsonData = json.decode(responseData.body);
      setState(() {
        _prediction = jsonData['prediction'];
      });
    } else {
      setState(() {
        _prediction = 'Error: ${response.statusCode}';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Image Picker Example'),
      ),
      body: Center(
        child: Column(
          children: <Widget>[
            _image == null
                ? Text('No image selected.')
                : Image.file(_image!),
            ElevatedButton(
              onPressed: getImage,
              child: Text('Pick Image'),
            ),
            ElevatedButton(
              onPressed: () {
                if (_image != null) {
                  uploadImage(_image!);
                }
              },
              child: Text('Upload Image and Predict'),
            ),
            Text(_prediction),
          ],
        ),
      ),
    );
  }
}
