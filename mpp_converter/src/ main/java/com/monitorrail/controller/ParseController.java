package com.monitorrail.controller;

import com.monitorrail.service.MppParseService;
import com.monitorrail.util.CryptoUtil;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import javax.crypto.SecretKey;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class ParseController {

    private final MppParseService parseService;

    @Value("${monitorrail.api.key:}")
    private String apiKey;

    public ParseController(MppParseService parseService) {
        this.parseService = parseService;
    }

    @PostMapping("/parse-mpp")
    public ResponseEntity<?> parseMpp(@RequestHeader(value="X-API-KEY", required=false) String key,
                                      @RequestParam("file") MultipartFile file) {
        try {
            if (apiKey != null && !apiKey.isEmpty() && (key == null || !apiKey.equals(key))) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("error","Invalid API key"));
            }

            byte[] bytes = file.getBytes();
            CryptoUtil.EncryptedResult enc = CryptoUtil.encryptBytes(bytes);

            Map<String,Object> json = parseService.parseMppEncrypted(enc.cipherText, enc.iv, enc.key);
            // null sensitive key
            enc.key = null;

            return ResponseEntity.ok(json);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("error", e.getMessage()));
        }
    }
}

