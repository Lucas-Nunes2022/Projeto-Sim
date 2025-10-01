using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Editor_Rotas.Models;

namespace Editor_Rotas.Services
{
    public static class Client
    {
        private static readonly HttpClient httpClient = new HttpClient();

        public static async Task<Dictionary<string, object>> Register(string nome, string email, string password)
        {
            try
            {
                var payload = new { nome, email, password };
                var content = new StringContent(JsonConvert.SerializeObject(payload), Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync($"{Constantes.BASE_URL}/register", content);
                var body = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<Dictionary<string, object>>(body);
            }
            catch (Exception ex)
            {
                return new Dictionary<string, object>
                {
                    { "success", false },
                    { "message", $"Erro de conexão: {ex.Message}" }
                };
            }
        }

        public static async Task<Dictionary<string, object>> Login(string email, string password)
        {
            try
            {
                var payload = new { email, password };
                var content = new StringContent(JsonConvert.SerializeObject(payload), Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync($"{Constantes.BASE_URL}/login", content);
                var body = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<Dictionary<string, object>>(body);
            }
            catch (Exception ex)
            {
                return new Dictionary<string, object>
                {
                    { "success", false },
                    { "message", $"Erro de conexão: {ex.Message}" }
                };
            }
        }

        public static async Task<Dictionary<string, object>> ListFiles(string fileType = "routes")
        {
            try
            {
                var response = await httpClient.GetAsync($"{Constantes.BASE_URL}/list/{fileType}");
                var body = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<Dictionary<string, object>>(body);
            }
            catch (Exception ex)
            {
                return new Dictionary<string, object>
                {
                    { "success", false },
                    { "message", $"Erro de conexão: {ex.Message}" }
                };
            }
        }

        public static async Task<Dictionary<string, object>> Upload(string dirPath, string userId)
        {
            try
            {
                if (!Directory.Exists(dirPath))
                {
                    return new Dictionary<string, object>
                    {
                        { "success", false },
                        { "message", "O upload aceita apenas diretórios" }
                    };
                }

                string tempFile = Path.GetTempFileName();
                string zipPath = Path.ChangeExtension(tempFile, ".zip");
                if (File.Exists(zipPath)) File.Delete(zipPath);

                ZipFile.CreateFromDirectory(dirPath, zipPath, CompressionLevel.Fastest, true);

                using (var form = new MultipartFormDataContent())
                {
                    var stream = File.OpenRead(zipPath);
                    var fileContent = new StreamContent(stream);
                    fileContent.Headers.ContentType = new MediaTypeHeaderValue("application/zip");

                    form.Add(fileContent, "file", Path.GetFileName(zipPath));
                    form.Add(new StringContent(userId), "user_id");

                    var response = await httpClient.PostAsync($"{Constantes.BASE_URL}/upload/routes", form);
                    var body = await response.Content.ReadAsStringAsync();

                    return JsonConvert.DeserializeObject<Dictionary<string, object>>(body);
                }
            }
            catch (Exception ex)
            {
                return new Dictionary<string, object>
                {
                    { "success", false },
                    { "message", $"Erro de conexão: {ex.Message}" }
                };
            }
        }

        public static async Task<Dictionary<string, object>> Download(string fileName, string savePath, string fileType = "routes")
        {
            try
            {
                // sempre usar singular "route", igual no Python
                var check = await httpClient.GetStringAsync($"{Constantes.BASE_URL}/files/route");
                var checkResult = JsonConvert.DeserializeObject<Dictionary<string, object>>(check);

                if (checkResult == null || !checkResult.ContainsKey("success") || !(bool)checkResult["success"])
                {
                    return checkResult ?? new Dictionary<string, object>
                    {
                        { "success", false },
                        { "message", "Erro ao verificar arquivos no servidor" }
                    };
                }

                var fileUrl = $"{Constantes.BASE_URL}/data/{fileType}/{fileName}";
                var resp = await httpClient.GetAsync(fileUrl);

                if (resp.IsSuccessStatusCode)
                {
                    string zipPath = Path.Combine(savePath, fileName);
                    using (var fs = new FileStream(zipPath, FileMode.Create, FileAccess.Write))
                    {
                        await resp.Content.CopyToAsync(fs);
                    }

                    string extractDir = Path.Combine(savePath, Path.GetFileNameWithoutExtension(fileName));
                    ZipFile.ExtractToDirectory(zipPath, extractDir, true);

                    File.Delete(zipPath);
                    return new Dictionary<string, object>
                    {
                        { "success", true },
                        { "message", $"{fileName} baixado e extraído em {extractDir}" }
                    };
                }

                return new Dictionary<string, object>
                {
                    { "success", false },
                    { "message", "Falha ao baixar arquivo" }
                };
            }
            catch (Exception ex)
            {
                return new Dictionary<string, object>
                {
                    { "success", false },
                    { "message", $"Erro de conexão: {ex.Message}" }
                };
            }
        }

        public static async Task<Dictionary<string, object>> Delete(string fileName, string userId, string fileType = "routes")
        {
            try
            {
                var payload = new { file_name = fileName, user_id = userId };
                var content = new StringContent(JsonConvert.SerializeObject(payload), Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync($"{Constantes.BASE_URL}/delete/{fileType}", content);
                var body = await response.Content.ReadAsStringAsync();

                return JsonConvert.DeserializeObject<Dictionary<string, object>>(body);
            }
            catch (Exception ex)
            {
                return new Dictionary<string, object>
                {
                    { "success", false },
                    { "message", $"Erro de conexão: {ex.Message}" }
                };
            }
        }
    }
}
