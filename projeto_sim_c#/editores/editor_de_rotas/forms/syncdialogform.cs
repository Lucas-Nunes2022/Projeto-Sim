using System;
using System.IO;
using System.Threading.Tasks;
using System.Windows.Forms;
using Editor_Rotas.Models;
using Editor_Rotas.Services;

namespace Editor_Rotas.Forms
{
    public partial class SyncDialogForm : Form
    {
        private Panel panelMain;
        private Panel panelLogin;
        private Panel panelRegister;
        private Panel panelFiles;

        private TextBox loginEmail;
        private TextBox loginPassword;
        private TextBox registerNome;
        private TextBox registerEmail;
        private TextBox registerPassword;
        private ListBox listCtrl;
        private Button btnUpload;
        private Button btnDelete;

        private string fileType = "routes";

        public SyncDialogForm()
        {
            BuildUI();
            ShowPanel(panelMain);
        }

        private void BuildUI()
        {
            this.Text = "Sincronização";
            this.Width = 500;
            this.Height = 450;
            this.StartPosition = FormStartPosition.CenterParent;

            panelMain = new Panel { Dock = DockStyle.Fill };
            panelLogin = new Panel { Dock = DockStyle.Fill };
            panelRegister = new Panel { Dock = DockStyle.Fill };
            panelFiles = new Panel { Dock = DockStyle.Fill };

            BuildMainPanel();
            BuildLoginPanel();
            BuildRegisterPanel();
            BuildFilesPanel();

            this.Controls.Add(panelMain);
            this.Controls.Add(panelLogin);
            this.Controls.Add(panelRegister);
            this.Controls.Add(panelFiles);
        }

        private void ShowPanel(Panel panel)
        {
            panelMain.Visible = false;
            panelLogin.Visible = false;
            panelRegister.Visible = false;
            panelFiles.Visible = false;
            panel.Visible = true;

            if (panel == panelFiles)
            {
                if (Constantes.SESSION.Role == "admin" && fileType == "routes")
                {
                    btnUpload.Visible = true;
                    btnDelete.Visible = true;
                }
                else
                {
                    btnUpload.Visible = false;
                    btnDelete.Visible = false;
                }
            }
        }

        private void BuildMainPanel()
        {
            var layout = new FlowLayoutPanel { Dock = DockStyle.Fill, FlowDirection = FlowDirection.TopDown, Padding = new Padding(20) };
            var btnLogin = new Button { Text = "Entrar", Height = 40, Dock = DockStyle.Top };
            var btnRegister = new Button { Text = "Criar Conta", Height = 40, Dock = DockStyle.Top };
            var btnClose = new Button { Text = "Fechar", Height = 40, Dock = DockStyle.Top };

            btnLogin.Click += (s, e) => ShowPanel(panelLogin);
            btnRegister.Click += (s, e) => ShowPanel(panelRegister);
            btnClose.Click += (s, e) => this.Close();

            layout.Controls.Add(new Label { Text = "O que deseja fazer?" });
            layout.Controls.Add(btnLogin);
            layout.Controls.Add(btnRegister);
            layout.Controls.Add(btnClose);

            panelMain.Controls.Add(layout);
        }

        private void BuildLoginPanel()
        {
            var layout = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 2 };
            loginEmail = new TextBox();
            loginPassword = new TextBox { UseSystemPasswordChar = true };

            var btnLogin = new Button { Text = "Login" };
            var btnBack = new Button { Text = "Voltar" };

            btnLogin.Click += async (s, e) => await OnLogin();
            btnBack.Click += (s, e) => ShowPanel(panelMain);

            layout.Controls.Add(new Label { Text = "E-mail:" }, 0, 0);
            layout.Controls.Add(loginEmail, 1, 0);
            layout.Controls.Add(new Label { Text = "Senha:" }, 0, 1);
            layout.Controls.Add(loginPassword, 1, 1);
            layout.Controls.Add(btnLogin, 0, 2);
            layout.Controls.Add(btnBack, 1, 2);

            panelLogin.Controls.Add(layout);
        }

        private void BuildRegisterPanel()
        {
            var layout = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 2 };
            registerNome = new TextBox();
            registerEmail = new TextBox();
            registerPassword = new TextBox { UseSystemPasswordChar = true };

            var btnRegister = new Button { Text = "Criar Conta" };
            var btnBack = new Button { Text = "Voltar" };

            btnRegister.Click += async (s, e) => await OnRegister();
            btnBack.Click += (s, e) => ShowPanel(panelMain);

            layout.Controls.Add(new Label { Text = "Nome:" }, 0, 0);
            layout.Controls.Add(registerNome, 1, 0);
            layout.Controls.Add(new Label { Text = "E-mail:" }, 0, 1);
            layout.Controls.Add(registerEmail, 1, 1);
            layout.Controls.Add(new Label { Text = "Senha:" }, 0, 2);
            layout.Controls.Add(registerPassword, 1, 2);
            layout.Controls.Add(btnRegister, 0, 3);
            layout.Controls.Add(btnBack, 1, 3);

            panelRegister.Controls.Add(layout);
        }

        private void BuildFilesPanel()
        {
            var layout = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 1 };
            listCtrl = new ListBox();

            var btnDownload = new Button { Text = "Baixar selecionado" };
            btnUpload = new Button { Text = "Enviar pasta de rota" };
            btnDelete = new Button { Text = "Deletar selecionado" };
            var btnBack = new Button { Text = "Voltar ao Menu Principal" };
            var btnClose = new Button { Text = "Fechar" };

            btnDownload.Click += async (s, e) => await OnDownload();
            btnUpload.Click += async (s, e) => await OnUpload();
            btnDelete.Click += async (s, e) => await OnDelete();
            btnBack.Click += (s, e) => ShowPanel(panelMain);
            btnClose.Click += (s, e) => this.Close();

            layout.Controls.Add(new Label { Text = "Arquivos disponíveis:" });
            layout.Controls.Add(listCtrl);
            layout.Controls.Add(btnDownload);
            layout.Controls.Add(btnUpload);
            layout.Controls.Add(btnDelete);
            layout.Controls.Add(btnBack);
            layout.Controls.Add(btnClose);

            panelFiles.Controls.Add(layout);
        }

        private async Task OnLogin()
        {
            var result = await Client.Login(loginEmail.Text.Trim(), loginPassword.Text.Trim());
            if (!result.ContainsKey("success") || !(bool)result["success"])
            {
                MessageBox.Show($"Erro no login: {result["message"]}", "Erro");
                return;
            }

            Constantes.SESSION.LoggedIn = true;
            Constantes.SESSION.UserId = result["user_id"].ToString();
            Constantes.SESSION.Role = result["role"].ToString();
            Constantes.SESSION.Nome = result["nome"].ToString();
            Constantes.SESSION.Email = loginEmail.Text.Trim();

            MessageBox.Show($"Bem-vindo, {Constantes.SESSION.Nome}!", "Sucesso");
            ShowPanel(panelFiles);
            await LoadFiles();
        }

        private async Task OnRegister()
        {
            var result = await Client.Register(registerNome.Text.Trim(), registerEmail.Text.Trim(), registerPassword.Text.Trim());
            if (result.ContainsKey("success") && (bool)result["success"])
            {
                await OnLogin();
            }
            else
            {
                MessageBox.Show($"Erro ao criar conta: {result["message"]}", "Erro");
            }
        }

        private async Task LoadFiles()
        {
            var result = await Client.ListFiles(fileType);
            if (!result.ContainsKey("success") || !(bool)result["success"])
            {
                MessageBox.Show($"Erro ao listar arquivos: {result["message"]}", "Erro");
                return;
            }

            listCtrl.Items.Clear();
            if (result.ContainsKey("files"))
            {
                if (result["files"] is Newtonsoft.Json.Linq.JArray arr)
                {
                    foreach (var f in arr) listCtrl.Items.Add(f.ToString());
                }
            }
        }

        private async Task OnDownload()
        {
            if (listCtrl.SelectedItem == null) return;
            string fileName = listCtrl.SelectedItem.ToString();
            string saveDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "lucas_producoes", "simbuss", fileType);

            Directory.CreateDirectory(saveDir);

            var result = await Client.Download(fileName, saveDir, fileType);
            if (result.ContainsKey("success") && (bool)result["success"])
                MessageBox.Show($"{fileName} baixado com sucesso em {saveDir}", "Sucesso");
            else
                MessageBox.Show($"Erro ao baixar: {result["message"]}", "Erro");

            await LoadFiles();
        }

        private async Task OnUpload()
        {
            using (var fbd = new FolderBrowserDialog())
            {
                fbd.Description = "Selecione a pasta da rota";
                fbd.SelectedPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                    "lucas_producoes", "simbuss", "routes");

                if (fbd.ShowDialog() == DialogResult.OK)
                {
                    var result = await Client.Upload(fbd.SelectedPath, Constantes.SESSION.UserId);
                    if (result.ContainsKey("success") && (bool)result["success"])
                        MessageBox.Show($"Pasta {fbd.SelectedPath} enviada com sucesso!", "Servidor");
                    else
                        MessageBox.Show($"Erro ao enviar: {result["message"]}", "Erro");

                    await LoadFiles();
                }
            }
        }

        private async Task OnDelete()
        {
            if (listCtrl.SelectedItem == null) return;
            string fileName = listCtrl.SelectedItem.ToString();
            var confirm = MessageBox.Show($"Tem certeza que deseja deletar '{fileName}' do servidor?",
                "Confirmar deleção", MessageBoxButtons.YesNo, MessageBoxIcon.Warning);
            if (confirm != DialogResult.Yes) return;

            var result = await Client.Delete(fileName, Constantes.SESSION.UserId, fileType);
            if (result.ContainsKey("success") && (bool)result["success"])
                MessageBox.Show($"Arquivo {fileName} deletado com sucesso!", "Sucesso");
            else
                MessageBox.Show($"Erro ao deletar: {result["message"]}", "Erro");

            await LoadFiles();
        }
    }
}
