<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

if (isset($_POST['token'])) {
    // open socket to token.php
    $socket = fsockopen('127.0.0.1', 80);
    if (!$socket) {
        die('Cannot open socket');
    }
    $request = "GET /token.php HTTP/1.1\r\n";
    $request .= "Host: localhost\r\n";
    // Add here the submitted token with a single newline to make it work with HTTP/1.1
    $request .= "X-API-Token: {$_POST['token']}\r\n";
    $request .= "Connection: close\r\n\r\n";
    fwrite($socket, $request);
    $response = '';
    while (!feof($socket)) {
        $response .= fgets($socket);
    }
    fclose($socket);
    // parse response
    $index = strpos($response, "\r\n\r\n");
    $response = substr($response, $index + 4);
}
?>
<!DOCTYPE html>
<html>
    <head>
        <title>The Backend</title>
        <link rel="stylesheet" href="/css/bootstrap.min.css">
        <script src="/js/bootstrap.bundle.min.js"></script>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container-fluid">
                <a class="navbar-brand" href="/">The Backend</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNavAltMarkup">
                    <div class="navbar-nav">
                        <a class="nav-link" href="/token.php">Token</a>
                        <a class="nav-link" href="/flag.php">Flag</a>
                    </div>
                </div>
            </div>
        </nav>
        <main class="container mt-4">
            <h1>Interfaccia per provare i token</h1>
            <form method="post">
            <textarea class="form-control" name="token" rows="1"><?php echo $_POST['token'] ?? ''; ?></textarea>
                <input type="submit" class="btn btn-primary mt-4" value="Prova">
            </form>
            <?php if (isset($response)): ?>
                <p class="mt-2">Il server risponde:</p>
                <pre><?php echo htmlspecialchars($response); ?></pre>
            <?php endif; ?>
        </main>
    </body>
</html>
