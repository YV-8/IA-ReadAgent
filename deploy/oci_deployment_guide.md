# Guía de despliegue en OCI (Oracle Cloud Infrastructure)

Esta guía despliega la app de Streamlit en una instancia Compute de OCI (sirve con el
**Always Free tier**, no hace falta pagar nada).

## 1. Crear la instancia Compute

1. Entrá a la [consola de OCI](https://cloud.oracle.com/) → **Compute → Instances → Create Instance**.
2. Elegí una imagen **Canonical Ubuntu 22.04** (Always Free elegible).
3. Shape: `VM.Standard.E2.1.Micro` o `VM.Standard.A1.Flex` (ambos entran en el free tier).
4. En "Add SSH keys", subí tu clave pública (o generá un par nuevo desde la consola y
   descargá la privada — la vas a necesitar para conectarte).
5. Creá la instancia y anotá su **IP pública**.

## 2. Abrir el puerto 8501 (el que usa Streamlit)

Por defecto, OCI bloquea todo el tráfico entrante salvo SSH (22).

1. Andá a la instancia → **Subnet** → **Security Lists** (o **Network Security Groups** si
   usaste una VCN con NSG).
2. Agregá una **Ingress Rule**:
   - Source CIDR: `0.0.0.0/0`
   - Protocolo: TCP
   - Puerto destino: `8501`
3. Conectate por SSH a la instancia y abrí también el firewall interno de Ubuntu:
   ```bash
   sudo ufw allow 8501/tcp
   ```

## 3. Instalar dependencias en la instancia

```bash
ssh -i tu-clave-privada.key ubuntu@<IP_PUBLICA_DE_LA_INSTANCIA>

sudo apt update && sudo apt install -y python3-pip python3-venv git

git clone https://github.com/<tu-usuario>/<tu-repo>.git
cd <tu-repo>

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4. Configurar las variables de entorno

```bash
cp .env.example .env
nano .env   # completá GOOGLE_API_KEY y, si hace falta, las rutas a tus documentos
```

Subí (o copiá con `scp`) tu CSV y tu PDF reales a la carpeta `data/` de la instancia —
no los subas al repo público si son documentos sensibles.

## 5. Levantar la app (prueba rápida)

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Entrá desde tu navegador a `http://<IP_PUBLICA_DE_LA_INSTANCIA>:8501` — ahí ya deberías
ver el chat funcionando. **Esa es la captura de pantalla que va en el README.**

## 6. (Recomendado) Dejarla corriendo como servicio con systemd

Para que la app siga corriendo aunque cierres la sesión SSH o se reinicie la máquina:

```bash
sudo tee /etc/systemd/system/rag-agent.service > /dev/null <<'EOF'
[Unit]
Description=Agente RAG - Streamlit
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/<tu-repo>
Environment="PATH=/home/ubuntu/<tu-repo>/venv/bin"
ExecStart=/home/ubuntu/<tu-repo>/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now rag-agent.service
sudo systemctl status rag-agent.service
```

## 7. Evidencia para el README

Una vez que la app responda correctamente desde `http://<IP_PUBLICA>:8501`:

- Tomá una captura de pantalla del chat con una pregunta real respondida.
- Guardala en `deploy/screenshot.png` (o donde prefieras) y enlazala desde el README.
- Opcionalmente, dejá la IP pública anotada (si vas a mantener la instancia activa) para
  que quien evalúe el proyecto pueda entrar directamente.

> **Nota de seguridad:** si el CSV/PDF contiene información sensible, no los subas al
> repositorio público de GitHub — solo a la instancia de OCI (agregalos a `.gitignore`).
