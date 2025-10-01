using System;
using System.Windows.Forms;
using Editor_Rotas.Forms;

namespace Editor_Rotas
{
    static class Program
    {
        [STAThread]
        static void Main()
        {
            ApplicationConfiguration.Initialize();
            Application.Run(new MainForm());
        }
    }
}
