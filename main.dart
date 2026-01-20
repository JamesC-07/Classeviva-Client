import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';
import 'dart:async';

void main() {
  runApp(ClassevivaApp());
}

class ClassevivaApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Classeviva',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        brightness: Brightness.dark,
      ),
      home: SplashScreen(),
    );
  }
}

class SplashScreen extends StatefulWidget {
  @override
  _SplashScreenState createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkCredentials();
  }

  Future<void> _checkCredentials() async {
    final prefs = await SharedPreferences.getInstance();
    final username = prefs.getString('username');
    final password = prefs.getString('password');

    if (username != null && password != null) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => LoginScreen(
            autoLogin: true,
            savedUsername: username,
            savedPassword: password,
          ),
        ),
      );
    } else {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => LoginScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: CircularProgressIndicator(),
      ),
    );
  }
}

class LoginScreen extends StatefulWidget {
  final bool autoLogin;
  final String? savedUsername;
  final String? savedPassword;

  LoginScreen({
    this.autoLogin = false,
    this.savedUsername,
    this.savedPassword,
  });

  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  String _errorMessage = '';

  @override
  void initState() {
    super.initState();
    if (widget.autoLogin) {
      _usernameController.text = widget.savedUsername ?? '';
      _passwordController.text = widget.savedPassword ?? '';
      _login();
    }
  }

  Future<void> _login() async {
    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });

    final username = _usernameController.text.trim();
    final password = _passwordController.text;

    if (username.isEmpty || password.isEmpty) {
      setState(() {
        _errorMessage = 'Inserisci username e password';
        _isLoading = false;
      });
      return;
    }

    try {
      final api = ClassevivaAPI(username, password);
      await api.login();
      
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('username', username);
      await prefs.setString('password', password);

      final carta = await api.getCarta();
      final nome = carta['firstName'] ?? username;

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => MainScreen(api: api, nome: nome),
        ),
      );
    } catch (e) {
      setState(() {
        _errorMessage = 'Login fallito: ${e.toString()}';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: EdgeInsets.all(24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  'Classeviva Client',
                  style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
                ),
                SizedBox(height: 48),
                ConstrainedBox(
                  constraints: BoxConstraints(maxWidth: 400),
                  child: Column(
                    children: [
                      TextField(
                        controller: _usernameController,
                        decoration: InputDecoration(
                          labelText: 'Username (es. S1234567C)',
                          border: OutlineInputBorder(),
                        ),
                        enabled: !_isLoading,
                      ),
                      SizedBox(height: 16),
                      TextField(
                        controller: _passwordController,
                        decoration: InputDecoration(
                          labelText: 'Password',
                          border: OutlineInputBorder(),
                        ),
                        obscureText: true,
                        enabled: !_isLoading,
                      ),
                      SizedBox(height: 24),
                      SizedBox(
                        width: double.infinity,
                        height: 50,
                        child: ElevatedButton(
                          onPressed: _isLoading ? null : _login,
                          child: _isLoading
                              ? CircularProgressIndicator(color: Colors.white)
                              : Text('Accedi', style: TextStyle(fontSize: 18)),
                        ),
                      ),
                      if (_errorMessage.isNotEmpty) ...[
                        SizedBox(height: 16),
                        Text(
                          _errorMessage,
                          style: TextStyle(color: Colors.red),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class MainScreen extends StatefulWidget {
  final ClassevivaAPI api;
  final String nome;

  MainScreen({required this.api, required this.nome});

  @override
  _MainScreenState createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;
  List<dynamic> _voti = [];
  List<dynamic> _assenze = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      print('Inizio caricamento dati...');
      
      final voti = await widget.api.getVoti();
      final assenze = await widget.api.getAssenze();
      
      print('Voti ricevuti: ${voti.length}');
      print('Assenze ricevute: ${assenze.length}');
      
      setState(() {
        _voti = voti;
        _assenze = assenze;
        _isLoading = false;
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Caricati ${voti.length} voti e ${assenze.length} assenze'),
          duration: Duration(seconds: 3),
        ),
      );
      
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: Text('Errore caricamento'),
          content: SingleChildScrollView(
            child: Text('$e'),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text('OK'),
            ),
          ],
        ),
      );
    }
  }

  Future<void> _logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('username');
    await prefs.remove('password');
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => LoginScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Benvenuto, ${widget.nome}'),
        actions: [
          IconButton(
            icon: Icon(Icons.logout),
            onPressed: _logout,
          ),
        ],
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator())
          : IndexedStack(
              index: _selectedIndex,
              children: [
                VotiTab(voti: _voti),
                AssenzeTab(assenze: _assenze),
              ],
            ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) => setState(() => _selectedIndex = index),
        items: [
          BottomNavigationBarItem(icon: Icon(Icons.grade), label: 'Voti'),
          BottomNavigationBarItem(icon: Icon(Icons.event_busy), label: 'Assenze'),
        ],
      ),
    );
  }
}

class VotiTab extends StatelessWidget {
  final List<dynamic> voti;

  VotiTab({required this.voti});

  int _determineQuarter(String date) {
    try {
      final d = DateTime.parse(date);
      // Q1: settembre-gennaio (fino al 28)
      if (d.month >= 9 || (d.month == 1 && d.day <= 28)) return 1;
      // Q2: gennaio (dopo il 28) - giugno
      if ((d.month == 1 && d.day > 28) || (d.month >= 2 && d.month <= 6)) return 2;
    } catch (_) {}
    return 0;
  }

  double? _parseVoto(String valore) {
    try {
      return double.parse(valore.replaceAll(',', '.').replaceAll('+', '').replaceAll('-', '').replaceAll('½', '.5'));
    } catch (_) {
      return null;
    }
  }

  Map<String, dynamic> _calculateStats() {
    List<double> votiQ1 = [];
    List<double> votiQ2 = [];
    List<double> votiTotali = [];
    Map<String, List<double>> votiPerMateria = {};
    Map<String, Map<int, int>> conteggioVotiPerQuadrimestre = {};
    Map<String, Map<int, List<double>>> votiPerMateriaPerQuadrimestre = {}; // AGGIUNTO

    for (var voto in voti) {
      final colorCode = voto['color'] ?? '';
      if (colorCode == 'blue') continue;

      final valore = voto['displayValue'] ?? voto['decimalValue']?.toString() ?? '';
      final val = _parseVoto(valore);
      if (val == null) continue;

      final data = voto['evtDate'] ?? '';
      final quarter = _determineQuarter(data);
      final materia = voto['subjectDesc'] ?? 'N/A';

      votiTotali.add(val);
      
      if (quarter == 1) votiQ1.add(val);
      if (quarter == 2) votiQ2.add(val);

      votiPerMateria.putIfAbsent(materia, () => []).add(val);
      
      conteggioVotiPerQuadrimestre.putIfAbsent(materia, () => {1: 0, 2: 0});
      if (quarter == 1) conteggioVotiPerQuadrimestre[materia]![1] = (conteggioVotiPerQuadrimestre[materia]![1] ?? 0) + 1;
      if (quarter == 2) conteggioVotiPerQuadrimestre[materia]![2] = (conteggioVotiPerQuadrimestre[materia]![2] ?? 0) + 1;
      
      // traccia i voti per materia per quadrimestre
      votiPerMateriaPerQuadrimestre.putIfAbsent(materia, () => {1: [], 2: []});
      if (quarter == 1) votiPerMateriaPerQuadrimestre[materia]![1]!.add(val);
      if (quarter == 2) votiPerMateriaPerQuadrimestre[materia]![2]!.add(val);
    }

    double calcMedia(List<double> list) => list.isEmpty ? 0 : list.reduce((a, b) => a + b) / list.length;

    Map<String, double> medie = {};
    Map<String, Map<int, double>> mediePerQuadrimestre = {}; 
    
    votiPerMateria.forEach((materia, voti) {
      medie[materia] = calcMedia(voti);
    });
    
    // calcola medie per quadrimestre
    votiPerMateriaPerQuadrimestre.forEach((materia, quadrimestri) {
      mediePerQuadrimestre[materia] = {
        1: calcMedia(quadrimestri[1] ?? []),
        2: calcMedia(quadrimestri[2] ?? []),
      };
    });

    return {
      'mediaTotale': calcMedia(votiTotali),
      'mediaQ1': calcMedia(votiQ1),
      'mediaQ2': calcMedia(votiQ2),
      'medie': medie,
      'conteggi': conteggioVotiPerQuadrimestre,
      'mediePerQuadrimestre': mediePerQuadrimestre, 
    };
  }

  @override
  Widget build(BuildContext context) {
    if (voti.isEmpty) {
      return Center(child: Text('Nessun voto disponibile'));
    }

    final stats = _calculateStats();
    final mediaTotale = stats['mediaTotale'] as double;
    final mediaQ1 = stats['mediaQ1'] as double;
    final mediaQ2 = stats['mediaQ2'] as double;
    final medie = stats['medie'] as Map<String, double>;
    final conteggi = stats['conteggi'] as Map<String, Map<int, int>>;
    final mediePerQuadrimestre = stats['mediePerQuadrimestre'] as Map<String, Map<int, double>>; // AGGIUNTO

    final now = DateTime.now();
    final currentQuarter = (now.month >= 9 || (now.month == 1 && now.day <= 28)) ? 1 : 2;

    final votiOrdinati = List.from(voti);
    votiOrdinati.sort((a, b) {
      try {
        final dateA = DateTime.parse(a['evtDate'] ?? '');
        final dateB = DateTime.parse(b['evtDate'] ?? '');
        return dateB.compareTo(dateA);
      } catch (_) {
        return 0;
      }
    });

    // AGGIUNTO: ordina le materie per media del quadrimestre corrente
    final materieOrdinate = medie.entries.toList()
      ..sort((a, b) {
        final mediaA = mediePerQuadrimestre[a.key]?[currentQuarter] ?? 0;
        final mediaB = mediePerQuadrimestre[b.key]?[currentQuarter] ?? 0;
        return mediaB.compareTo(mediaA); // Decrescente
      });

    return ListView(
      padding: EdgeInsets.all(16),
      children: [
        // Card medie generali
        Card(
          color: Colors.blue.withOpacity(0.1),
          child: Padding(
            padding: EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('MEDIE GENERALI', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: _MediaCard(label: 'Media Totale', media: mediaTotale),
                    ),
                    SizedBox(width: 12),
                    Expanded(
                      child: _MediaCard(label: 'Q1', media: mediaQ1),
                    ),
                    SizedBox(width: 12),
                    Expanded(
                      child: _MediaCard(label: 'Q2', media: mediaQ2),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        SizedBox(height: 16),

        // Card medie per materia con istogramma - MODIFICATO
        Card(
          color: Colors.purple.withOpacity(0.1),
          child: Padding(
            padding: EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('MEDIE PER MATERIA (Q$currentQuarter)', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                SizedBox(height: 16),
                ...materieOrdinate.map((entry) { // CAMBIATO da medie.entries
                  final materia = entry.key;
                  final mediaTotaleMateria = entry.value;
                  final mediaQuadrimestre = mediePerQuadrimestre[materia]?[currentQuarter] ?? 0; // AGGIUNTO
                  final numVotiQ1 = conteggi[materia]?[1] ?? 0;
                  final numVotiQ2 = conteggi[materia]?[2] ?? 0;
                  final numVotiQuadrimestre = currentQuarter == 1 ? numVotiQ1 : numVotiQ2;
                  final hasWarning = numVotiQuadrimestre < 3;

                  return GestureDetector( // AGGIUNTO
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => MateriaDetailScreen(
                            materia: materia,
                            voti: voti,
                          ),
                        ),
                      );
                    },
                    child: Padding(
                      padding: EdgeInsets.only(bottom: 12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: Text(
                                  materia,
                                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
                                ),
                              ),
                              if (hasWarning)
                                Container(
                                  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: Colors.red.withOpacity(0.2),
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Row(
                                    children: [
                                      Icon(Icons.warning, color: Colors.red, size: 14),
                                      SizedBox(width: 4),
                                      Text(
                                        'solo $numVotiQuadrimestre voti',
                                        style: TextStyle(color: Colors.red, fontSize: 11),
                                      ),
                                    ],
                                  ),
                                ),
                              SizedBox(width: 8),
                              Text(
                                mediaQuadrimestre > 0 ? mediaQuadrimestre.toStringAsFixed(2) : 'N/A', // CAMBIATO
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: mediaQuadrimestre >= 6 ? Colors.green : Colors.red, // CAMBIATO
                                ),
                              ),
                            ],
                          ),
                          SizedBox(height: 4),
                          Stack(
                            children: [
                              Container(
                                height: 8,
                                decoration: BoxDecoration(
                                  color: Colors.grey.withOpacity(0.3),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                              ),
                              FractionallySizedBox(
                                widthFactor: (mediaQuadrimestre / 10).clamp(0.0, 1.0), // CAMBIATO
                                child: Container(
                                  height: 8,
                                  decoration: BoxDecoration(
                                    color: mediaQuadrimestre >= 6 ? Colors.green : Colors.red, // CAMBIATO
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ],
            ),
          ),
        ),
        SizedBox(height: 16),

        // Lista voti ordinati - RESTA UGUALE
        Text(
          'TUTTI I VOTI',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        SizedBox(height: 12),
        ...votiOrdinati.map((voto) {
          final materia = voto['subjectDesc'] ?? 'N/A';
          final valore = voto['displayValue'] ?? voto['decimalValue']?.toString() ?? 'N/A';
          final data = voto['evtDate'] ?? 'N/A';
          final tipo = voto['componentDesc'] ?? 'N/A';
          final nota = voto['notesForFamily'] ?? '';
          final colorCode = voto['color'] ?? '';
          final nonConta = colorCode == 'blue';
          final quarter = _determineQuarter(data);

          Color votoColor;
          if (nonConta) {
            votoColor = Colors.blue;
          } else {
            final val = _parseVoto(valore);
            votoColor = val != null ? (val >= 6 ? Colors.green : Colors.red) : Colors.grey;
          }

          return Card(
            margin: EdgeInsets.only(bottom: 8),
            child: Padding(
              padding: EdgeInsets.all(12),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 80,
                    child: Column(
                      children: [
                        Text(
                          valore,
                          style: TextStyle(
                            fontSize: 32,
                            fontWeight: FontWeight.bold,
                            color: votoColor,
                          ),
                        ),
                        SizedBox(height: 4),
                        Text(
                          '$data${quarter > 0 ? ' [Q$quarter]' : ''}',
                          style: TextStyle(fontSize: 10),
                        ),
                      ],
                    ),
                  ),
                  SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          materia,
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                        SizedBox(height: 4),
                        Text(tipo, style: TextStyle(fontSize: 13)),
                        if (nota.isNotEmpty) ...[
                          SizedBox(height: 4),
                          Text(
                            nota,
                            style: TextStyle(fontSize: 11, color: Colors.grey),
                          ),
                        ],
                      ],
                    ),
                  ),
                ],
              ),
            ),
          );
        }).toList(),
      ],
    );
  }
}

class _MediaCard extends StatelessWidget {
  final String label;
  final double media;

  _MediaCard({required this.label, required this.media});

  @override
  Widget build(BuildContext context) {
    final color = media >= 6 ? Colors.green : Colors.red;
    return Container(
      padding: EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[400])),
          SizedBox(height: 4),
          Text(
            media > 0 ? media.toStringAsFixed(2) : 'N/A',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: color),
          ),
        ],
      ),
    );
  }
}

class MateriaDetailScreen extends StatelessWidget {
  final String materia;
  final List<dynamic> voti;

  MateriaDetailScreen({
    required this.materia,
    required this.voti,
  });

  int _determineQuarter(String date) {
    try {
      final d = DateTime.parse(date);
      if (d.month >= 9 || (d.month == 1 && d.day <= 28)) return 1;
      if ((d.month == 1 && d.day > 28) || (d.month >= 2 && d.month <= 6)) return 2;
    } catch (_) {}
    return 0;
  }

  double? _parseVoto(String valore) {
    try {
      return double.parse(valore.replaceAll(',', '.').replaceAll('+', '').replaceAll('-', '').replaceAll('½', '.5'));
    } catch (_) {
      return null;
    }
  }

  Map<String, dynamic> _calcStats() {
    List<double> votiQ1 = [];
    List<double> votiQ2 = [];
    List<dynamic> votiMateria = [];

    for (var voto in voti) {
      final materiaVoto = voto['subjectDesc'] ?? '';
      if (materiaVoto != materia) continue;

      final colorCode = voto['color'] ?? '';
      if (colorCode == 'blue') continue;

      votiMateria.add(voto);

      final valore = voto['displayValue'] ?? voto['decimalValue']?.toString() ?? '';
      final val = _parseVoto(valore);
      if (val == null) continue;

      final data = voto['evtDate'] ?? '';
      final quarter = _determineQuarter(data);

      if (quarter == 1) votiQ1.add(val);
      if (quarter == 2) votiQ2.add(val);
    }

    votiMateria.sort((a, b) {
      try {
        final dateA = DateTime.parse(a['evtDate'] ?? '');
        final dateB = DateTime.parse(b['evtDate'] ?? '');
        return dateB.compareTo(dateA);
      } catch (_) {
        return 0;
      }
    });

    double calcMedia(List<double> list) => 
      list.isEmpty ? 0 : list.reduce((a, b) => a + b) / list.length;

    return {
      'mediaQ1': calcMedia(votiQ1),
      'mediaQ2': calcMedia(votiQ2),
      'mediaTotale': calcMedia([...votiQ1, ...votiQ2]),
      'votiMateria': votiMateria,
    };
  }

  @override
  Widget build(BuildContext context) {
    final stats = _calcStats();
    final mediaQ1 = stats['mediaQ1'] as double;
    final mediaQ2 = stats['mediaQ2'] as double;
    final mediaTotale = stats['mediaTotale'] as double;
    final votiMateria = stats['votiMateria'] as List<dynamic>;

    return Scaffold(
      appBar: AppBar(
        title: Text(materia),
      ),
      body: ListView(
        padding: EdgeInsets.all(16),
        children: [
          Card(
            color: Colors.blue.withOpacity(0.1),
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Column(
                children: [
                  Text('MEDIE', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(child: _MediaCard(label: 'Totale', media: mediaTotale)),
                      SizedBox(width: 12),
                      Expanded(child: _MediaCard(label: 'Q1', media: mediaQ1)),
                      SizedBox(width: 12),
                      Expanded(child: _MediaCard(label: 'Q2', media: mediaQ2)),
                    ],
                  ),
                ],
              ),
            ),
          ),
          SizedBox(height: 16),
          Text('TUTTI I VOTI', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          SizedBox(height: 12),
          ...votiMateria.map((voto) {
            final valore = voto['displayValue'] ?? voto['decimalValue']?.toString() ?? 'N/A';
            final data = voto['evtDate'] ?? 'N/A';
            final tipo = voto['componentDesc'] ?? 'N/A';
            final nota = voto['notesForFamily'] ?? '';
            final quarter = _determineQuarter(data);

            final val = _parseVoto(valore);
            final votoColor = val != null ? (val >= 6 ? Colors.green : Colors.red) : Colors.grey;

            return Card(
              margin: EdgeInsets.only(bottom: 8),
              child: ListTile(
                leading: Container(
                  width: 50,
                  height: 50,
                  decoration: BoxDecoration(
                    color: votoColor.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Center(
                    child: Text(
                      valore,
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: votoColor,
                      ),
                    ),
                  ),
                ),
                title: Text('$tipo - $data${quarter > 0 ? ' [Q$quarter]' : ''}'),
                subtitle: nota.isNotEmpty ? Text(nota, style: TextStyle(fontSize: 11)) : null,
              ),
            );
          }).toList(),
        ],
      ),
    );
  }
}

class AssenzeTab extends StatelessWidget {
  final List<dynamic> assenze;

  AssenzeTab({required this.assenze});

  Map<String, int> _countAssenze() {
    int totali = 0, ritardi = 0, uscite = 0;
    for (var a in assenze) {
      final code = a['evtCode'] ?? '';
      if (code == 'ABA0') totali++;
      else if (code == 'ABR0') ritardi++;
      else if (code == 'ABU0') uscite++;
    }
    return {'totali': totali, 'ritardi': ritardi, 'uscite': uscite};
  }

  Map<String, double> _calculateAbsenceProgress() {
    // Anno scolastico: 15 settembre - 10 giugno
    final now = DateTime.now();
    final annoCorrente = now.month >= 9 ? now.year : now.year - 1;
    final inizioAnno = DateTime(annoCorrente, 9, 15);
    final fineAnno = DateTime(annoCorrente + 1, 6, 10);
    
    final giorniTotali = fineAnno.difference(inizioAnno).inDays;
    final giorniTrascorsi = now.difference(inizioAnno).inDays.clamp(0, giorniTotali);
    
    final percentualeAnno = (giorniTrascorsi / giorniTotali * 100).clamp(0.0, 100.0);
    
    // Massimo 25% di assenze (circa 50 giorni su 200 giorni di scuola)
    final giorniScuolaTotali = 200.0;
    final massimoAssenze = giorniScuolaTotali * 0.25;
    
    final counts = _countAssenze();
    final assenzeEffettive = counts['totali']!.toDouble();
    final percentualeAssenze = (assenzeEffettive / massimoAssenze * 100).clamp(0.0, 100.0);
    
    return {
      'percentualeAnno': percentualeAnno,
      'percentualeAssenze': percentualeAssenze,
      'assenzeEffettive': assenzeEffettive,
      'massimoAssenze': massimoAssenze,
    };
  }

  @override
  Widget build(BuildContext context) {
    if (assenze.isEmpty) {
      return Center(child: Text('Nessun dato sulle assenze'));
    }

    final counts = _countAssenze();
    final progress = _calculateAbsenceProgress();

    return ListView(
      padding: EdgeInsets.all(16),
      children: [
        // Grafico progresso assenze
        Card(
          color: Colors.orange.withOpacity(0.1),
          child: Padding(
            padding: EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'PROGRESSO ASSENZE',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                SizedBox(height: 16),
                Text(
                  'Anno trascorso: ${progress['percentualeAnno']!.toStringAsFixed(1)}%',
                  style: TextStyle(fontSize: 14, color: Colors.grey[400]),
                ),
                SizedBox(height: 8),
                Stack(
                  children: [
                    Container(
                      height: 24,
                      decoration: BoxDecoration(
                        color: Colors.grey.withOpacity(0.3),
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    FractionallySizedBox(
                      widthFactor: progress['percentualeAnno']! / 100,
                      child: Container(
                        height: 24,
                        decoration: BoxDecoration(
                          color: Colors.blue,
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 24),
                Text(
                  'Assenze: ${progress['assenzeEffettive']!.toInt()} / ${progress['massimoAssenze']!.toInt()} (${progress['percentualeAssenze']!.toStringAsFixed(1)}%)',
                  style: TextStyle(fontSize: 14, color: Colors.grey[400]),
                ),
                SizedBox(height: 8),
                Stack(
                  children: [
                    Container(
                      height: 24,
                      decoration: BoxDecoration(
                        color: Colors.grey.withOpacity(0.3),
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    FractionallySizedBox(
                      widthFactor: progress['percentualeAssenze']! / 100,
                      child: Container(
                        height: 24,
                        decoration: BoxDecoration(
                          color: progress['percentualeAssenze']! > 80
                              ? Colors.red
                              : progress['percentualeAssenze']! > 50
                                  ? Colors.orange
                                  : Colors.green,
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ],
                ),
                if (progress['percentualeAssenze']! > progress['percentualeAnno']!) ...[
                  SizedBox(height: 12),
                  Container(
                    padding: EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.red.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.warning, color: Colors.red, size: 16),
                        SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'Attenzione: stai facendo più assenze del dovuto!',
                            style: TextStyle(color: Colors.red, fontSize: 12),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
        SizedBox(height: 16),

        Text(
          'STATISTICHE ASSENZE',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _StatCard(
                label: 'Assenze',
                value: '${counts['totali']}',
                color: Colors.red,
              ),
            ),
            SizedBox(width: 12),
            Expanded(
              child: _StatCard(
                label: 'Ritardi',
                value: '${counts['ritardi']}',
                color: Colors.orange,
              ),
            ),
          ],
        ),
        SizedBox(height: 12),
        _StatCard(
          label: 'Uscite Anticipate',
          value: '${counts['uscite']}',
          color: Colors.deepOrange,
        ),
        SizedBox(height: 24),
        Text(
          'DETTAGLIO',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        SizedBox(height: 12),
        ...assenze.take(20).map((a) {
          final code = a['evtCode'] ?? '';
          final data = a['evtDate'] ?? 'N/A';
          final giust = a['isJustified'] ?? false;

          String tipo;
          Color color;
          if (code == 'ABA0') {
            tipo = 'Assenza';
            color = Colors.red;
          } else if (code == 'ABR0') {
            tipo = 'Ritardo';
            color = Colors.orange;
          } else if (code == 'ABU0') {
            tipo = 'Uscita Anticipata';
            color = Colors.deepOrange;
          } else {
            tipo = 'Altro';
            color = Colors.grey;
          }

          return Card(
            margin: EdgeInsets.only(bottom: 8),
            child: ListTile(
              leading: Icon(Icons.event_busy, color: color),
              title: Text(tipo),
              subtitle: Text(data),
              trailing: Container(
                padding: EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                decoration: BoxDecoration(
                  color: giust ? Colors.green.withOpacity(0.2) : Colors.orange.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  giust ? 'Giustificata' : 'Da giustificare',
                  style: TextStyle(
                    color: giust ? Colors.green : Colors.orange,
                    fontSize: 12,
                  ),
                ),
              ),
            ),
          );
        }).toList(),
      ],
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  _StatCard({required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[400])),
          SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: color),
          ),
        ],
      ),
    );
  }
}

class ClassevivaAPI {
  final String username;
  final String password;
  String? _token;
  String? _userId;

  ClassevivaAPI(this.username, this.password);

  Future<void> login() async {
    try {
      final requestBody = '{"ident": null, "pass": "$password", "uid": "$username"}';
      
      final response = await http.post(
        Uri.parse('https://web.spaggiari.eu/rest/v1/auth/login'),
        headers: {
          'Content-Type': 'application/json',
          'Z-Dev-Apikey': 'Tg1NWEwNGIgIC0K',
          'User-Agent': 'CVVS/std/4.2.3 Android/12',
        },
        body: requestBody,
      ).timeout(Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _token = data['token'];
        
        String rawIdent = data['ident'] ?? '';
        _userId = rawIdent.replaceAll(RegExp(r'[^0-9]'), ''); 
        
        if (_token == null || _userId!.isEmpty) {
          throw Exception('Token o ID utente non valido nella risposta');
        }
        
        print('Login effettuato. UserID numerico: $_userId');
      } else if (response.statusCode == 422) {
        throw Exception('Username o password non validi');
      } else {
        throw Exception('Login fallito (${response.statusCode})');
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> getCarta() async {
    final response = await http.get(
      Uri.parse('https://web.spaggiari.eu/rest/v1/students/$_userId/card'),
      headers: {
        'Z-Dev-Apikey': 'Tg1NWEwNGIgIC0K',
        'Z-Auth-Token': _token!,
        'User-Agent': 'CVVS/std/4.2.3 Android/12',
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['card'] ?? {};
    } else {
      throw Exception('Errore recupero profilo (Carta): ${response.statusCode}');
    }
  }

  Future<List<dynamic>> getVoti() async {
    final response = await http.get(
      Uri.parse('https://web.spaggiari.eu/rest/v1/students/$_userId/grades'),
      headers: {
        'Z-Dev-Apikey': 'Tg1NWEwNGIgIC0K',
        'Z-Auth-Token': _token!,
        'User-Agent': 'CVVS/std/4.2.3 Android/12',
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['grades'] ?? [];
    } else {
      throw Exception('Errore voti: ${response.statusCode} - ${response.body}');
    }
  }

  Future<List<dynamic>> getAssenze() async {
    final response = await http.get(
      Uri.parse('https://web.spaggiari.eu/rest/v1/students/$_userId/absences/details'),
      headers: {
        'Z-Dev-Apikey': 'Tg1NWEwNGIgIC0K',
        'Z-Auth-Token': _token!,
        'User-Agent': 'CVVS/std/4.2.3 Android/12',
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['events'] ?? [];
    } else {
      throw Exception('Errore assenze: ${response.statusCode} - ${response.body}');
    }
  }
}