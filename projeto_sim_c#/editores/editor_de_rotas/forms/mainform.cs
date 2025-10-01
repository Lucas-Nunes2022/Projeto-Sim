using System;
using System.IO;
using System.Text;
using System.Windows.Forms;
using Newtonsoft.Json;
using Editor_Rotas.Models;
using Editor_Rotas.Utils;

namespace Editor_Rotas.Forms
{
    public partial class MainForm : Form
    {
        public MainForm()
        {
            BuildUI();
        }

        private void BuildUI()
        {
            this.Text = $"Editor de Rotas v{Constantes.VERSAO}";
            this.Width = 400;
            this.Height = 250;
            this.StartPosition = FormStartPosition.CenterScreen;

            var btnNova = new Button { Text = "Criar nova rota", Dock = DockStyle.Top, Height = 40 };
            var btnEditar = new Button { Text = "Editar rota existente", Dock = DockStyle.Top, Height = 40 };
            var btnSync = new Button { Text = "Sincronizar com servidor", Dock = DockStyle.Top, Height = 40 };
            var btnSair = new Button { Text = "Sair", Dock = DockStyle.Top, Height = 40 };

            btnNova.Click += BtnNova_Click;
            btnEditar.Click += BtnEditar_Click;
            btnSync.Click += BtnSync_Click;
            btnSair.Click += (s, e) => this.Close();

            var layout = new FlowLayoutPanel
            {
                Dock = DockStyle.Fill,
                FlowDirection = FlowDirection.TopDown,
                Padding = new Padding(20)
            };

            layout.Controls.Add(btnNova);
            layout.Controls.Add(btnEditar);
            layout.Controls.Add(btnSync);
            layout.Controls.Add(btnSair);

            this.Controls.Add(layout);
        }

        private void BtnNova_Click(object sender, EventArgs e)
        {
            var rota = new Rota();
            var editor = new EditorRotaForm(rota, null);
            editor.ShowDialog();
        }

        private void BtnEditar_Click(object sender, EventArgs e)
        {
            using (var fbd = new FolderBrowserDialog())
            {
                fbd.Description = "Escolha a pasta da rota";
                fbd.SelectedPath = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                    "lucas_producoes", "simbuss", "routes"
                );

                if (fbd.ShowDialog() == DialogResult.OK)
                {
                    var pasta = new DirectoryInfo(fbd.SelectedPath);
                    var rouFiles = pasta.GetFiles("*.rou");
                    if (rouFiles.Length == 0)
                    {
                        MessageBox.Show("Nenhum arquivo .rou encontrado na pasta!", "Erro",
                            MessageBoxButtons.OK, MessageBoxIcon.Error);
                        return;
                    }

                    try
                    {
                        string dadosEnc = File.ReadAllText(rouFiles[0].FullName, Encoding.UTF8);
                        string dadosJson = FernetHelper.Decrypt(dadosEnc);
                        var rota = JsonConvert.DeserializeObject<Rota>(dadosJson);
                        var editor = new EditorRotaForm(rota, pasta.FullName);
                        editor.ShowDialog();
                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show($"Erro ao carregar rota: {ex.Message}", "Erro",
                            MessageBoxButtons.OK, MessageBoxIcon.Error);
                    }
                }
            }
        }

        private void BtnSync_Click(object sender, EventArgs e)
        {
            var sync = new SyncDialogForm();
            sync.ShowDialog();
        }
    }
}
