namespace Editor_Rotas.Models
{
    public static class Constantes
    {
        public static readonly string VEICULO_KEY = "I2LiFD4mSt5EbyyZPqfjafmDy4tpb1Ctmb5U8XnwzL0=";
        public static readonly string FERNET_KEY = "2hxPv0NeMyu-NUv334e6Ltb6MY0K9aFi-dC6yxJSyGs=";

        public const string VERSAO = "2.0";

        public const string IP = "130.61.53.157";
        public const string PORTA = "5000";
        public static readonly string BASE_URL = $"http://{IP}:{PORTA}";

        public static Session SESSION = new Session();
    }

    public class Session
    {
        public bool LoggedIn { get; set; } = false;
        public string? UserId { get; set; }
        public string? Nome { get; set; }
        public string? Role { get; set; }
        public string? Email { get; set; }
    }
}
