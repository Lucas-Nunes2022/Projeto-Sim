namespace Editor_Rotas.Models
{
    public class Elemento
    {
        public string Tipo { get; set; } = "";
        public double DistanciaP0 { get; set; } = 0.0;
        public string Superficie { get; set; } = "";
        public int Ordem { get; set; } = 0;
        public string Nome { get; set; } = "";
        public string Direcao { get; set; } = "";
        public double Angulacao { get; set; } = 0.0;
        public string RuaDireita { get; set; } = "";
        public string RuaEsquerda { get; set; } = "";
        public string TipoSemaforo { get; set; } = "";
        public string RuaPrincipal { get; set; } = "";
        public int LimVelocidade { get; set; } = 0;
    }
}
