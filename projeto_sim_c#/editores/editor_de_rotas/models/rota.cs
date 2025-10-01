using System.Collections.Generic;

namespace Editor_Rotas.Models
{
    public class Rota
    {
        public string IdRota { get; set; } = "";
        public string NomeRota { get; set; } = "";
        public string Operador { get; set; } = "";
        public string TipoVia { get; set; } = "";
        public string TipoRota { get; set; } = "";
        public string PontoInicial { get; set; } = "";
        public string PontoFinal { get; set; } = "";
        public double DistanciaP0Pf { get; set; } = 0.0;
        public List<string> Veiculos { get; set; } = new();
        public int TmpEstimado { get; set; } = 0;
        public string TipoTrafego { get; set; } = "";
        public int IntervaloMin { get; set; } = 0;
        public List<Elemento> Elementos { get; set; } = new();
    }
}
