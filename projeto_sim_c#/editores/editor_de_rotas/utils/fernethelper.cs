using System;
using Cryptography;

namespace Editor_Rotas.Utils
{
    public static class FernetHelper
    {
        private static string RawKey => Editor_Rotas.Models.Constantes.FERNET_KEY;

        static string NormalizeKey(string key)
        {
            if (key == null) throw new ArgumentNullException(nameof(key));
            var fixedKey = key.Trim().Replace('-', '+').Replace('_', '/');
            while (fixedKey.Length % 4 != 0) fixedKey += "=";
            var bytes = Convert.FromBase64String(fixedKey);
            if (bytes.Length != 32)
                throw new ArgumentException($"Fernet key decodificada precisa ter 32 bytes, veio {bytes.Length}.", nameof(key));
            return fixedKey;
        }

        static string CleanToken(string token)
        {
            if (token == null) throw new ArgumentNullException(nameof(token));
            return token.Trim().Replace("\r", "").Replace("\n", "");
        }

        public static string Encrypt(string plainText)
        {
            var key = NormalizeKey(RawKey);
            try
            {
                // assinatura mais comum: (plaintext, key)
                return Fernet.Encrypt(plainText, key);
            }
            catch (ArgumentException)
            {
                // algumas builds expõem (key, plaintext)
                return Fernet.Encrypt(key, plainText);
            }
        }

        public static string Decrypt(string token, TimeSpan? ttl = null)
        {
            var key = NormalizeKey(RawKey);
            var clean = CleanToken(token);

            try
            {
                // tentativa 1: (token, key, ttl)
                return Fernet.Decrypt(clean, key, ttl);
            }
            catch (ArgumentException ex) when (ex.ParamName == "key" || ex.Message.Contains("Decoded key field"))
            {
                // se a lib entendeu 'token' como 'key', tenta (key, token, ttl)
                return Fernet.Decrypt(key, clean, ttl);
            }
        }
    }
}
