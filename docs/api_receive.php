<?php

// 
// ** Receive media notification from wee-media-receiver
// **
// Expected body
// {
//      "media_id": "uploads/test_2", 
//      "new_media_id": "uploads/test_2.webm", 
//      "status": "PROCESSED", 
//      "post_id": 1, 
//      "metadata": {
//          "drawings": "1.1618", 
//          "hentai": "0.0783", 
//          "neutral": "95.439", 
//          "porn": "0.0208", 
//          "sexy": "3.3001000000000005"
//      }
// }
ignore_user_abort(true);
define("EXPECTED_AUTH", "41a70d9013a3b2d279df17683a55d932");
define("AUTH_HEADER", "HTTP_X_WEEMEDIA_AUTH");



function api_exit($code, $message)
{
    ob_start();
    header("Content-Type: application/json");
    http_response_code($code);
    echo json_encode(array('status' => $message));
    header('Connection: close');
    header('Content-Length: ' . ob_get_length());
    ob_end_flush();
    @ob_flush();
    if ($code >= 400) {
        exit;
    }
}

$auth = "";
if (array_key_exists(AUTH_HEADER, $_SERVER)) {
    $auth = $_SERVER[AUTH_HEADER];
    if ($auth != EXPECTED_AUTH) {
        api_exit(403, "Invalid authorization header");
    }
} else {
    api_exit(403, "Missing authorization header");
}

$contents = file_get_contents('php://input');
$payload = json_decode($contents, true);

if (json_last_error() !== JSON_ERROR_NONE) {
    api_exit(400, 'Invalid JSON');
}

try {
    foreach (array("media_id", "new_media_id", "status", "post_id", "metadata") as $key) {
        if (!array_key_exists($key, $payload)) {
            api_exit(400, "Missing $key");
        }
    }
    if (!array_key_exists("media_id", $payload)) {
        api_exit(400, "Missing media_id");
    }
    $media_id = $payload['media_id'];
    $new_media_id = $payload['new_media_id'];
    $status = $payload['status'];
    $post_id = $payload['post_id'];
    $metadata = array(
        'drawings' => floatval($payload['metadata']['drawings']),
        'hentai' => floatval($payload['metadata']['hentai']),
        'neutral' => floatval($payload['metadata']['neutral']),
        'porn' => floatval($payload['metadata']['porn']),
        'sexy' => floatval($payload['metadata']['sexy'])
    );
    api_exit(202, 'accepted', array('payload' => $payload, 'contents' => $contents, 'metadata' => $metadata));
    process_received_media($media_id, $new_media_id, $status, $post_id, $metadata);
} catch (Exception $e) {
    api_exit(400, 'Invalid JSON: ' . $e->getMessage());
}

// Here the response was sent to the client and we can run the data update

function process_received_media($media_id, $new_media_id, $status, $post_id, $metadata)
{
    sleep(5);
    error_log("Received media notification: " . json_encode(array(
        'media_id' => $media_id,
        'new_media_id' => $new_media_id,
        'status' => $status,
        'post_id' => $post_id,
        'metadata' => $metadata
    )));
}
