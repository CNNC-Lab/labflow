# Manual release steps (user executes after review)

These steps push the labflow repo to GitHub, create the v0.1.0 release, enable GitHub Pages, and install labflow globally.

**Prerequisite**: morning review of the local repo complete.

## 1. Create the remote repo (start PRIVATE)

```bash
cd ~/repos/labflow
gh repo create CNNC-Lab/labflow --private \
    --description "Opinionated scientific workflow manager — Hydra + Submitit + Snakemake glue for reproducible experiments and SLURM submission." \
    --source=. --push
```

Verify at https://github.com/CNNC-Lab/labflow (should show the code, private badge).

## 2. Tag v0.1.0 and push the tag

```bash
cd ~/repos/labflow
git tag -a v0.1.0 -m "v0.1.0 — initial release"
git push origin v0.1.0
```

## 3. Create GitHub release (still private; release is visible to org members)

```bash
gh release create v0.1.0 --repo CNNC-Lab/labflow \
    --title "v0.1.0 — initial release" \
    --notes "$(sed -n '/## \[0.1.0\]/,/## \[/{/## \[0.1.0\]/b;/## \[/b;p;}' CHANGELOG.md)"
```

## 4. Flip repo to public (after reviewing release looks right)

```bash
gh repo edit CNNC-Lab/labflow --visibility public --accept-visibility-change-consequences
```

## 5. Enable GitHub Pages

```bash
# After the docs workflow has run once on the pushed branch
gh api -X PUT "repos/CNNC-Lab/labflow/pages" \
    -f "source[branch]=gh-pages" -f "source[path]=/" 2>&1 | head -5
```

Verify at https://cnnc-lab.github.io/labflow/ within ~2 minutes.

## 6. Install labflow globally (or into your preferred env)

```bash
# Option A: install into a dedicated conda env (recommended for isolation)
conda create -n labflow-client python=3.12 -y
conda activate labflow-client
pip install -e ~/repos/labflow
labflow --version

# Option B: install into your nest-dev env
source ~/nest/activate_nest_dev.sh
pip install -e ~/repos/labflow

# Option C: user-level install
pip install --user -e ~/repos/labflow
```

## 7. Request Zenodo DOI (after release visible on public repo)

Log in to https://zenodo.org, link CNNC-Lab/labflow, set "Enable preservation", then push a new tag or re-publish the release. Zenodo mints DOI automatically. Copy the DOI badge into CITATION.cff.

## 8. Announce (optional)

- Update [[CLAUDE.md]] labflow row with the published URL
- Post to lab Slack / email lab members
- Update MEMORY.md entry with DOI
