package com.monitorrail.util;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import java.security.SecureRandom;
import java.util.Base64;

public class CryptoUtil {
    public static class EncryptedResult {
        public byte[] cipherText;
        public byte[] iv;
        public SecretKey key;
    }

    public static EncryptedResult encryptBytes(byte[] plain) throws Exception {
        KeyGenerator keyGen = KeyGenerator.getInstance("AES");
        keyGen.init(256);
        SecretKey key = keyGen.generateKey();

        byte[] iv = new byte[12];
        new SecureRandom().nextBytes(iv);

        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        GCMParameterSpec spec = new GCMParameterSpec(128, iv);
        cipher.init(Cipher.ENCRYPT_MODE, key, spec);
        byte[] cipherText = cipher.doFinal(plain);

        EncryptedResult er = new EncryptedResult();
        er.cipherText = cipherText;
        er.iv = iv;
        er.key = key;
        return er;
    }

    public static byte[] decryptBytes(byte[] cipherText, SecretKey key, byte[] iv) throws Exception {
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        GCMParameterSpec spec = new GCMParameterSpec(128, iv);
        cipher.init(Cipher.DECRYPT_MODE, key, spec);
        return cipher.doFinal(cipherText);
    }

    public static String keyToBase64(SecretKey key) {
        return Base64.getEncoder().encodeToString(key.getEncoded());
    }
}

