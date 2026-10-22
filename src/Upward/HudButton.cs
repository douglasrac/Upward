using Game.UI.MouseOvers;
using Game.UI.Session;
using HarmonyLib;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;

namespace Upward
{
    // Botao de verdade na barra do canto superior esquerdo: clona o "Grid Button" do jogo, entao tem
    // a mesma borda ao passar o mouse e a mesma caixa de descricao (TextMouseover com lockey proprio).
    // Cada botao do Upward entra a direita do ultimo que ja foi adicionado.
    internal class HudButton
    {
        private const string PREFIX = "Upward ";

        internal RectTransform Rect;
        private Image _frame;
        private Sprite _frameNormal, _frameLit;

        internal static HudButton Create(HUDLayers hud, string name, string icon, string tooltipKey, UnityAction onClick)
        {
            var go = Traverse.Create(hud).Field("_go").GetValue<GameObject>();
            Transform grid = go != null ? go.transform.Find("Panel Buttons/Grid Button") : null;
            if (grid == null)
            {
                Plugin.Log.LogWarning(name + ": botao Grid Button nao encontrado; sem botao na barra");
                return null;
            }

            // Referencia: o ultimo botao do Upward ja na barra, ou o proprio Grid
            Transform after = grid;
            foreach (Transform t in grid.parent)
            {
                if (t.name.StartsWith(PREFIX) && t.GetSiblingIndex() > after.GetSiblingIndex())
                {
                    after = t;
                }
            }

            GameObject clone = Object.Instantiate(grid.gameObject, grid.parent, false);
            clone.name = PREFIX + name;
            clone.transform.SetSiblingIndex(after.GetSiblingIndex() + 1);
            var result = new HudButton { Rect = clone.GetComponent<RectTransform>() };

            // Sem layout automatico na barra: coloca ao lado, com o mesmo espacamento entre botoes,
            // e alarga o fundo escuro da barra para cobrir o botao novo
            if (grid.parent.GetComponent<LayoutGroup>() == null)
            {
                var gridRect = grid.GetComponent<RectTransform>();
                float step = gridRect.rect.width;
                int idx = grid.GetSiblingIndex();
                if (idx > 0)
                {
                    var prev = grid.parent.GetChild(idx - 1).GetComponent<RectTransform>();
                    if (prev != null && prev.gameObject.activeSelf)
                    {
                        step = gridRect.anchoredPosition.x - prev.anchoredPosition.x;
                    }
                }
                result.Rect.anchoredPosition = after.GetComponent<RectTransform>().anchoredPosition + new Vector2(step, 0f);
                WidenBar(grid.parent, step, name);
            }

            var button = clone.GetComponent<Button>();
            button.onClick = new Button.ButtonClickedEvent();
            button.onClick.AddListener(onClick);

            foreach (var tip in clone.GetComponentsInChildren<TextMouseOverContext>(true))
            {
                tip.lockey = tooltipKey;
            }

            // A Image do botao e so a moldura (o jogo troca pela com borda ao passar o mouse); o icone do
            // grid e um glyph no texto filho. Esconde o texto e poe o nosso icone numa Image filha.
            foreach (Transform child in clone.transform)
            {
                child.gameObject.SetActive(false);
            }
            Sprite sprite = LoadSprite(icon);
            if (sprite != null)
            {
                var iconGo = new GameObject("Upward Icon", typeof(RectTransform));
                iconGo.transform.SetParent(clone.transform, false);
                var rt = iconGo.GetComponent<RectTransform>();
                rt.anchorMin = rt.anchorMax = new Vector2(0.5f, 0.5f);
                float size = Mathf.Min(result.Rect.rect.width, result.Rect.rect.height) * 0.55f;
                rt.sizeDelta = new Vector2(size, size);
                var img = iconGo.AddComponent<Image>();
                img.sprite = sprite;
                img.preserveAspect = true;
                img.raycastTarget = false;
            }

            result._frame = clone.GetComponent<Image>();
            result._frameNormal = result._frame != null ? result._frame.sprite : null;
            result._frameLit = button.spriteState.highlightedSprite;
            return result;
        }

        // Ligado (painel aberto, ferramenta ativa): fica com a borda acesa, como os botoes do jogo
        // quando selecionados
        internal void ShowLit(bool lit)
        {
            if (_frame != null && _frameLit != null)
            {
                _frame.sprite = lit ? _frameLit : _frameNormal;
            }
        }

        // Canto de baixo-esquerda do botao em coordenadas do IMGUI (canvas em Screen Space Overlay)
        internal Vector2 BelowLeft()
        {
            var corners = new Vector3[4];
            Rect.GetWorldCorners(corners); // 0 = baixo-esquerda
            return new Vector2(corners[0].x, Screen.height - corners[0].y + 6f);
        }

        // O fundo da barra pode ser a propria "Panel Buttons" ou o pai dela: alarga a primeira com Image,
        // mantendo a borda esquerda no lugar
        private static void WidenBar(Transform bar, float extra, string name)
        {
            for (Transform t = bar; t != null && t != bar.parent.parent; t = t.parent)
            {
                var img = t.GetComponent<Image>();
                var rt = t as RectTransform;
                if (img == null || rt == null || rt.anchorMin.x != rt.anchorMax.x)
                {
                    continue;
                }
                rt.sizeDelta += new Vector2(extra, 0f);
                rt.anchoredPosition += new Vector2(extra * rt.pivot.x, 0f);
                // Um filho ancorado em a (0 = esquerda, 1 = direita) andaria extra * a: devolve
                foreach (Transform child in t)
                {
                    var c = child as RectTransform;
                    if (c != null && c.anchorMin.x == c.anchorMax.x)
                    {
                        c.anchoredPosition -= new Vector2(extra * c.anchorMin.x, 0f);
                    }
                }
                Plugin.Log.LogInfo(name + ": fundo da barra '" + t.name + "' alargado em " + extra);
                return;
            }
            Plugin.Log.LogInfo(name + ": fundo da barra nao encontrado; botao fica ao lado");
        }

        private static Sprite LoadSprite(string relative)
        {
            Texture2D tex = UpwardAssets.LoadTexture(relative, TextureWrapMode.Clamp);
            return tex == null ? null : Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height), new Vector2(0.5f, 0.5f));
        }
    }
}
