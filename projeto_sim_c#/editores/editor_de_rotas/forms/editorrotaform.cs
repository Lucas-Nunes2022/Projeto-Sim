using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Windows.Forms;
using Newtonsoft.Json;
using Editor_Rotas.Models;
using Editor_Rotas.Utils;
using Editor_Rotas.Services;

namespace Editor_Rotas.Forms
{
    public partial class EditorRotaForm : Form
    {
        private Rota dados;
        private string pasta;

        private TabControl notebook;
        private TabPage page1;
        private TabPage page2;
        private TabPage page3;

        private TextBox id_rota;
        private TextBox nome_rota;
        private TextBox operador;
        private ComboBox tipo_via;
        private ComboBox tipo_rota;
        private TextBox ponto_inicial;
        private TextBox ponto_final;
        private TextBox distancia;
        private NumericUpDown tmp_estimado;
        private NumericUpDown intervalo_min;

        private ComboBox tipo_elem;
        private TextBox nome_elem;
        private ComboBox superficie_elem;
        private TextBox dist_elem;
        private ComboBox direcao_elem;
        private TextBox angulacao_elem;
        private TextBox rua_dir_elem;
        private TextBox rua_esq_elem;
        private ComboBox tipo_semaforo_elem;
        private ComboBox rua_principal;
        private TextBox lim_vel_elem;
        private ListBox lista_elementos;

        private ListBox lista_disponiveis;
        private ListBox lista_adicionados;

        public EditorRotaForm(Rota rota, string pasta)
        {
            this.dados = rota;
            this.pasta = pasta;
            BuildUI();
        }

        private void BuildUI()
        {
            this.Text = $"Editor de Rotas v{Constantes.VERSAO}";
            this.Width = 700;
            this.Height = 750;
            this.StartPosition = FormStartPosition.CenterScreen;

            notebook = new TabControl { Dock = DockStyle.Fill };
            page1 = new TabPage("Informações Gerais");
            page2 = new TabPage("Elementos");
            page3 = new TabPage("Veículos");

            notebook.TabPages.Add(page1);
            notebook.TabPages.Add(page2);
            notebook.TabPages.Add(page3);

            BuildPage1();
            BuildPage2();
            BuildPage3();

            this.Controls.Add(notebook);
        }

        private void BuildPage1()
        {
            var layout = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 2, RowCount = 11 };
            layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 40));
            layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 60));

            id_rota = new TextBox { Text = dados.IdRota };
            nome_rota = new TextBox { Text = dados.NomeRota };
            operador = new TextBox { Text = dados.Operador };
            tipo_via = new ComboBox { DropDownStyle = ComboBoxStyle.DropDownList };
            tipo_via.Items.AddRange(new[] { "Urbana", "Rodovia" });
            tipo_via.SelectedItem = dados.TipoVia;
            tipo_rota = new ComboBox { DropDownStyle = ComboBoxStyle.DropDownList };
            tipo_rota.Items.AddRange(new[] { "Municipal", "Intermunicipal", "Circular" });
            tipo_rota.SelectedItem = dados.TipoRota;
            ponto_inicial = new TextBox { Text = dados.PontoInicial };
            ponto_final = new TextBox { Text = dados.PontoFinal };
            distancia = new TextBox { Text = dados.DistanciaP0Pf.ToString() };
            tmp_estimado = new NumericUpDown { Minimum = 0, Maximum = 600, Value = dados.TmpEstimado };
            intervalo_min = new NumericUpDown { Minimum = 0, Maximum = 120, Value = dados.IntervaloMin };

            layout.Controls.Add(new Label { Text = "ID da Rota:" }, 0, 0);
            layout.Controls.Add(id_rota, 1, 0);
            layout.Controls.Add(new Label { Text = "Nome da Rota:" }, 0, 1);
            layout.Controls.Add(nome_rota, 1, 1);
            layout.Controls.Add(new Label { Text = "Operador:" }, 0, 2);
            layout.Controls.Add(operador, 1, 2);
            layout.Controls.Add(new Label { Text = "Tipo de Via:" }, 0, 3);
            layout.Controls.Add(tipo_via, 1, 3);
            layout.Controls.Add(new Label { Text = "Tipo de Rota:" }, 0, 4);
            layout.Controls.Add(tipo_rota, 1, 4);
            layout.Controls.Add(new Label { Text = "Ponto Inicial:" }, 0, 5);
            layout.Controls.Add(ponto_inicial, 1, 5);
            layout.Controls.Add(new Label { Text = "Ponto Final:" }, 0, 6);
            layout.Controls.Add(ponto_final, 1, 6);
            layout.Controls.Add(new Label { Text = "Distância total (km):" }, 0, 7);
            layout.Controls.Add(distancia, 1, 7);
            layout.Controls.Add(new Label { Text = "Tempo Estimado (min):" }, 0, 8);
            layout.Controls.Add(tmp_estimado, 1, 8);
            layout.Controls.Add(new Label { Text = "Intervalo (min):" }, 0, 9);
            layout.Controls.Add(intervalo_min, 1, 9);

            var btnProximo = new Button { Text = "Próximo", Dock = DockStyle.Bottom };
            btnProximo.Click += (s, e) => notebook.SelectedTab = page2;
            layout.Controls.Add(btnProximo, 1, 10);

            page1.Controls.Add(layout);
        }

        private void BuildPage2()
        {
            var layout = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 2, AutoScroll = true };
            layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 40));
            layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 60));

            tipo_elem = new ComboBox { DropDownStyle = ComboBoxStyle.DropDownList };
            tipo_elem.Items.AddRange(new[] { "Rua", "Curva", "Semáforo", "Parada", "Esquina" });

            nome_elem = new TextBox();
            superficie_elem = new ComboBox { DropDownStyle = ComboBoxStyle.DropDownList };
            superficie_elem.Items.AddRange(new[] { "Asfalto liso", "Asfalto com buracos", "Estrada de chão", "Grama" });
            dist_elem = new TextBox();
            direcao_elem = new ComboBox { DropDownStyle = ComboBoxStyle.DropDownList };
            direcao_elem.Items.AddRange(new[] { "Direita", "Esquerda" });
            angulacao_elem = new TextBox();
            rua_dir_elem = new TextBox();
            rua_esq_elem = new TextBox();
            tipo_semaforo_elem = new ComboBox { DropDownStyle = ComboBoxStyle.DropDownList };
            tipo_semaforo_elem.Items.AddRange(new[] { "Veicular", "Pedestre", "Inteligente" });
            rua_principal = new ComboBox { DropDownStyle = ComboBoxStyle.DropDownList };
            rua_principal.Items.AddRange(new[] { "Direita", "Esquerda", "Reto" });
            lim_vel_elem = new TextBox();

            lista_elementos = new ListBox();
            foreach (var e in dados.Elementos) lista_elementos.Items.Add(FormatElem(e));

            var btnAdd = new Button { Text = "Adicionar Elemento" };
            btnAdd.Click += AddElemento;
            var btnEdit = new Button { Text = "Editar" };
            btnEdit.Click += EditElemento;
            var btnRemove = new Button { Text = "Remover" };
            btnRemove.Click += RemoveElemento;

            var btnAnterior = new Button { Text = "Anterior" };
            btnAnterior.Click += (s, e) => notebook.SelectedTab = page1;
            var btnProximo = new Button { Text = "Próximo" };
            btnProximo.Click += (s, e) => notebook.SelectedTab = page3;

            layout.Controls.Add(new Label { Text = "Tipo do Elemento:" }, 0, 0);
            layout.Controls.Add(tipo_elem, 1, 0);
            layout.Controls.Add(new Label { Text = "Nome (Rua/Parada):" }, 0, 1);
            layout.Controls.Add(nome_elem, 1, 1);
            layout.Controls.Add(new Label { Text = "Superfície:" }, 0, 2);
            layout.Controls.Add(superficie_elem, 1, 2);
            layout.Controls.Add(new Label { Text = "Distância de P0 (km):" }, 0, 3);
            layout.Controls.Add(dist_elem, 1, 3);
            layout.Controls.Add(new Label { Text = "Direção da curva:" }, 0, 4);
            layout.Controls.Add(direcao_elem, 1, 4);
            layout.Controls.Add(new Label { Text = "Ângulo da curva (graus):" }, 0, 5);
            layout.Controls.Add(angulacao_elem, 1, 5);
            layout.Controls.Add(new Label { Text = "Rua à Direita:" }, 0, 6);
            layout.Controls.Add(rua_dir_elem, 1, 6);
            layout.Controls.Add(new Label { Text = "Rua à Esquerda:" }, 0, 7);
            layout.Controls.Add(rua_esq_elem, 1, 7);
            layout.Controls.Add(new Label { Text = "Tipo de Semáforo:" }, 0, 8);
            layout.Controls.Add(tipo_semaforo_elem, 1, 8);
            layout.Controls.Add(new Label { Text = "Limite de velocidade (km/h):" }, 0, 9);
            layout.Controls.Add(lim_vel_elem, 1, 9);

            layout.Controls.Add(btnAdd, 1, 10);
            layout.Controls.Add(lista_elementos, 0, 11);
            layout.SetColumnSpan(lista_elementos, 2);
            layout.Controls.Add(btnEdit, 0, 12);
            layout.Controls.Add(btnRemove, 1, 12);
            layout.Controls.Add(btnAnterior, 0, 13);
            layout.Controls.Add(btnProximo, 1, 13);

            page2.Controls.Add(layout);
        }

        private void BuildPage3()
        {
            var layout = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 2 };
            layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50));
            layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50));

            lista_disponiveis = new ListBox();
            foreach (var dir in Directory.GetDirectories(Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "lucas_producoes", "simbuss", "vehicles")))
            {
                var files = Directory.GetFiles(dir, "*.vel");
                if (files.Length > 0) lista_disponiveis.Items.Add(Path.GetFileName(dir));
            }

            lista_adicionados = new ListBox();
            foreach (var v in dados.Veiculos) lista_adicionados.Items.Add(v);

            var btnAdd = new Button { Text = "Adicionar à rota" };
            btnAdd.Click += AddVeiculo;
            var btnRemove = new Button { Text = "Remover da rota" };
            btnRemove.Click += RemoveVeiculo;
            var btnSalvar = new Button { Text = "Salvar Rota" };
            btnSalvar.Click += Salvar;
            var btnCancelar = new Button { Text = "Cancelar" };
            btnCancelar.Click += (s, e) => this.Close();

            layout.Controls.Add(new Label { Text = "Veículos disponíveis:" }, 0, 0);
            layout.Controls.Add(lista_disponiveis, 0, 1);
            layout.Controls.Add(btnAdd, 0, 2);
            layout.Controls.Add(new Label { Text = "Veículos adicionados:" }, 1, 0);
            layout.Controls.Add(lista_adicionados, 1, 1);
            layout.Controls.Add(btnRemove, 1, 2);
            layout.Controls.Add(btnSalvar, 0, 3);
            layout.Controls.Add(btnCancelar, 1, 3);

            page3.Controls.Add(layout);
        }

        private string FormatElem(Elemento e)
        {
            if (e.Tipo == "Rua") return $"Rua {e.Nome} ({e.Superficie}) - {e.DistanciaP0} km - {e.LimVelocidade} km/h";
            if (e.Tipo == "Parada") return $"Parada {e.Nome} - {e.DistanciaP0} km";
            if (e.Tipo == "Curva") return $"Curva {e.Direcao} {e.Angulacao}° ({e.Superficie}) - {e.DistanciaP0} km - {e.LimVelocidade} km/h";
            if (e.Tipo == "Semáforo") return $"Semáforo {e.TipoSemaforo} - {e.DistanciaP0} km";
            if (e.Tipo == "Esquina") return $"Esquina (segue pela {e.RuaPrincipal}) - {e.DistanciaP0} km";
            return $"{e.Tipo} - {e.DistanciaP0} km";
        }

        private void AddElemento(object sender, EventArgs e)
        {
            double.TryParse(dist_elem.Text, out var distanciaVal);
            double.TryParse(angulacao_elem.Text, out var angVal);
            double.TryParse(lim_vel_elem.Text, out var velVal);
            var elem = new Elemento
            {
                Tipo = tipo_elem.Text,
                Nome = nome_elem.Text,
                Superficie = superficie_elem.Text,
                DistanciaP0 = distanciaVal,
                Direcao = direcao_elem.Text,
                Angulacao = angVal,
                RuaDireita = rua_dir_elem.Text,
                RuaEsquerda = rua_esq_elem.Text,
                TipoSemaforo = tipo_semaforo_elem.Text,
                RuaPrincipal = rua_principal.Text,
                LimVelocidade = (int)velVal,
                Ordem = dados.Elementos.Count + 1
            };
            dados.Elementos.Add(elem);
            lista_elementos.Items.Add(FormatElem(elem));
        }

        private void EditElemento(object sender, EventArgs e)
        {
            if (lista_elementos.SelectedIndex == -1) return;
            dados.Elementos.RemoveAt(lista_elementos.SelectedIndex);
            lista_elementos.Items.RemoveAt(lista_elementos.SelectedIndex);
        }

        private void RemoveElemento(object sender, EventArgs e)
        {
            if (lista_elementos.SelectedIndex == -1) return;
            dados.Elementos.RemoveAt(lista_elementos.SelectedIndex);
            lista_elementos.Items.RemoveAt(lista_elementos.SelectedIndex);
        }

        private void AddVeiculo(object sender, EventArgs e)
        {
            if (lista_disponiveis.SelectedItem == null) return;
            string veic = lista_disponiveis.SelectedItem.ToString();
            if (!dados.Veiculos.Contains(veic))
            {
                dados.Veiculos.Add(veic);
                lista_adicionados.Items.Add(veic);
            }
        }

        private void RemoveVeiculo(object sender, EventArgs e)
        {
            if (lista_adicionados.SelectedItem == null) return;
            string veic = lista_adicionados.SelectedItem.ToString();
            dados.Veiculos.Remove(veic);
            lista_adicionados.Items.Remove(veic);
        }

        private void Salvar(object sender, EventArgs e)
        {
            dados.IdRota = id_rota.Text.Trim();
            dados.NomeRota = nome_rota.Text.Trim();
            dados.Operador = operador.Text.Trim();
            dados.TipoVia = tipo_via.Text.Trim();
            dados.TipoRota = tipo_rota.Text.Trim();
            dados.PontoInicial = ponto_inicial.Text.Trim();
            dados.PontoFinal = ponto_final.Text.Trim();
            double.TryParse(distancia.Text, out var distVal);
            dados.DistanciaP0Pf = distVal;
            dados.TmpEstimado = (int)tmp_estimado.Value;
            dados.IntervaloMin = (int)intervalo_min.Value;

            if (string.IsNullOrEmpty(dados.IdRota) || string.IsNullOrEmpty(dados.NomeRota))
            {
                MessageBox.Show("ID e Nome da rota não podem estar vazios!", "Erro",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            string basePath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "lucas_producoes", "simbuss", "routes", dados.IdRota);
            Directory.CreateDirectory(basePath);
            string arquivoRou = Path.Combine(basePath, $"{dados.IdRota}.rou");

            string dadosJson = JsonConvert.SerializeObject(dados, Formatting.Indented);
            string dadosEnc = FernetHelper.Encrypt(dadosJson);
            File.WriteAllText(arquivoRou, dadosEnc, Encoding.UTF8);

            if (Constantes.SESSION.LoggedIn)
            {
                if (Constantes.SESSION.Role != "admin")
                {
                    MessageBox.Show("Somente administradores podem enviar rotas ao servidor.", "Permissão negada",
                        MessageBoxButtons.OK, MessageBoxIcon.Warning);
                }
                else
                {
                    var result = Client.Upload(basePath, Constantes.SESSION.UserId).Result;
                    if (result.ContainsKey("success") && (bool)result["success"])
                        MessageBox.Show("Rota enviada com sucesso ao servidor!", "Servidor");
                    else
                        MessageBox.Show($"Erro ao enviar: {result["message"]}", "Servidor");
                }
            }
            else
            {
                MessageBox.Show("Você não está logado. Use 'Sincronizar com servidor' no menu inicial.",
                    "Login necessário", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }

            this.Close();
        }
    }
}
