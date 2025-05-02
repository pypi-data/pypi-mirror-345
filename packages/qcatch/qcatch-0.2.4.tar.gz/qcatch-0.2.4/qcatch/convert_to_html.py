import os
from bs4 import BeautifulSoup
import logging

from qcatch.plots_tables import *
from qcatch.input_processing import *

logger = logging.getLogger(__name__)

def create_plotly_plots(args, valid_bcs):
    """
    1.Load feature dump data from the alevin-frey quant output directory
    2.Create interactive Plotly plots
    """
    feature_dump_data = args.input.feature_dump_data
    map_json_data = args.input.map_json_data
    adata = args.input.mtx_data
    usa_mode = args.input.usa_mode
    
    # Filter cells with zero reads from featureDump data
    data = feature_dump_data[(feature_dump_data["deduplicated_reads"] >= 1) & (feature_dump_data["num_genes_expressed"] >= 1)]
    
    retained_data = data[data['barcodes'].isin(valid_bcs)]
    
    # Sort by "deduplicated_reads" and assign rank
    data = data.sort_values("deduplicated_reads", ascending=False).reset_index(drop=True)
    data["rank"] = data.index+1# 1-based rank
    
    # get filtered adata
    filtered_mask = adata.obs['barcodes'].isin(valid_bcs) if args.input.is_h5ad else adata.obs_names.isin(valid_bcs)
        # NOTE: safe but maybe time consuming
    filtered_adata = adata[filtered_mask, :].copy()

    # ---------------- Tab1 - Knee Plots ---------------
    fig_knee_1, fig_knee_2 = generate_knee_plots(data, valid_bcs)
    
    # ---------------- Generate summary table content ----------------
    all_mtx = None
    if usa_mode:
        # add up all layers
        all_mtx_filtered = filtered_adata.layers['spliced'] + filtered_adata.layers['unspliced'] + filtered_adata.layers['ambiguous']
    else: 
        all_mtx_filtered = filtered_adata.X
    # Get total detected genes for reatined cells
    total_detected_genes = (all_mtx_filtered > 0).sum(axis=0)  
    # Count genes with at least one UMI
    total_detected_genes = np.count_nonzero(total_detected_genes)  
    # calculate median genes per cell
    all_mtx_gene_per_cell = (all_mtx_filtered > 0).sum(axis=1).tolist()
    median_genes_per_cell = int(np.median(all_mtx_gene_per_cell))
    
    # get mapping rate
    mapping_rate = None
    if map_json_data:
        num_processed = map_json_data.get('num_processed') or map_json_data['num_reads']
        mapping_rate = round(map_json_data['num_mapped'] / num_processed * 100, 2)
    seq_saturation_value = generate_seq_saturation(retained_data)
        
    summary_table_html = generate_summary_table(data, valid_bcs, total_detected_genes, median_genes_per_cell, mapping_rate, seq_saturation_value)
    
    # ---------------- Tab2 - Barcode Frequency Plots ---------------
    fig_bc_freq_all_plots = barcode_frequency_plots(data, valid_bcs)
    # fig_bc_freq_UMI, fig_bc_freq_gene, fig_gene_UMI = barcode_frequency_plots(data)

    # ---------------- Tab3 - Collapsing ---------------
    # NOTE: use the retained data for umi_collapse plot
    fig_umi_dedup, mean_dedup_rate = umi_dedup(retained_data)
    
    # ---------------- Tab4 - Histogram of Genes Detected ---------------
    fig_hist_genes = generate_gene_histogram(data,is_all_cells=True)
    fig_hist_genes_filtered = generate_gene_histogram(retained_data,is_all_cells=False)
    # if our adata object doesn't already contain the gene symbol, then skip the mitochondrial plot.
    if ('gene_symbol' not in adata.var.columns):
        fig_mt = None
        fig_mt_filtered = None
    else:
        fig_mt = mitochondria_plot(adata, is_all_cells=True)
        fig_mt_filtered = mitochondria_plot(filtered_adata, is_all_cells=False)
    
    # ---------------- Tab5 - SUA plots ---------------
    if usa_mode:
        fig_SUA_bar_html, fig_S_ratio_html = generate_SUA_plots(adata,is_all_cells=True)
        fig_SUA_bar_filtered_html, fig_S_ratio_filtered_html = generate_SUA_plots(filtered_adata,is_all_cells=False)
    # ---------------- Tab6 - UMAP ---------------
    if not args.skip_umap_tsne:
        fig_umap, fig_tsne = umap_tsne_plot(filtered_adata)
        
    else:
        fig_umap = fig_tsne = None
        logger.info("🦦 Skipping UMAP and t-SNE plots as per user request.")
    
    # Convert plots to HTML div strings
    plots = {
        # ----tab1----(
        'knee_plot1-1': fig_knee_1.to_html(full_html=False, include_plotlyjs='cdn'),
        'knee_plot1-2': fig_knee_2.to_html(full_html=False, include_plotlyjs='cdn'),
        # ----tab2----
        'bc_freq_all_plots': fig_bc_freq_all_plots.to_html(full_html=False, include_plotlyjs='cdn'),
        # ----tab3----
        'hist_gene3-1':fig_hist_genes.to_html(full_html=False, include_plotlyjs="cdn"),
        # filtered data
        'hist_gene_filtered_3-1': fig_hist_genes_filtered.to_html(full_html=False, include_plotlyjs="cdn"),

        # ----tab4----
        'umi_dedup4': fig_umi_dedup.to_html(full_html=False, include_plotlyjs='cdn'),
        # ---tab6----
    }
    if fig_umap and fig_tsne:
        plots['umap_plot6-1'] = fig_umap.to_html(full_html=False, include_plotlyjs='cdn')
        plots['tsne_plot6-2'] = fig_tsne.to_html(full_html=False, include_plotlyjs='cdn')

    if fig_mt or fig_mt_filtered:
        #  2nd plot in tab3
        plots['fig_mt3-2'] = fig_mt.to_html(full_html=False, include_plotlyjs="cdn")
        plots['fig_mt_filtered_3-2'] = fig_mt_filtered.to_html(full_html=False, include_plotlyjs="cdn")
        
    # add key pair for SUA plots, is usa_mode is True
    if usa_mode:
        # ----tab5----
        plots['SUA_bar5-1'] = fig_SUA_bar_html
        plots['S_ratio5-2'] = fig_S_ratio_html
        plots['SUA_bar_filtered_5-1'] = fig_SUA_bar_filtered_html
        plots['S_ratio_filtered_5-2'] = fig_S_ratio_filtered_html
    plot_text_elements = (plots, summary_table_html)
    return plot_text_elements

def modify_html_with_plots(soup, output_html_path, plot_text_elements, table_htmls, warning_html, usa_mode):
    """
    Modify an HTML file to include Plotly plots, update text dynamically by ID, 
    and insert summary and log info tables.
    """
    plots, summary_table_html = plot_text_elements
    quant_json_table_html, permit_list_table_html = table_htmls
    
    updated_sections = []
    missing_sections = []

    # Updating plots
    for plot_id, plot_html in plots.items():
        plot_div = soup.find(id=plot_id)
        if plot_div:
            plot_div.clear()
            plot_div.append(BeautifulSoup(plot_html, 'html.parser'))
            updated_sections.append(plot_id)
        else:
            missing_sections.append(f"Plot '{plot_id}'")


    # Summary and log info tables
    for table_id, table_html in [
        ("summary_tbody", summary_table_html), 
        ("table-body-quant-log-info", quant_json_table_html),
        ("table-body-permit-log-info", permit_list_table_html)]:
        table_body = soup.find(id=table_id)
        if table_body:
            table_body.clear()
            table_body.append(BeautifulSoup(table_html, 'html.parser'))
            updated_sections.append(table_id)
        else:
            missing_sections.append(f"Table '{table_id}'")
    # Remove SUA tab if usa_mode is False
    if not usa_mode:
        sua_tab = soup.find(id="tab5_nav")  # Navbar tab
        sua_content = soup.find(id="tab5")  # Content section
        if sua_tab:
            sua_tab.decompose()
        if sua_content:
            sua_content.decompose()
    
    # Add warning section
    if warning_html.strip(): 
        warning_section = soup.find(id="qc-warning-container")
        if warning_section:
            warning_section.clear()
            warning_section.append(BeautifulSoup(warning_html, 'html.parser'))
            updated_sections.append("qc-warning-container")
        else:
            missing_sections.append("Warning section with id='qc-warning-container'")
            
        
    # Write the updated HTML to a new file
    with open(output_html_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))


    if missing_sections:
        for missing in missing_sections:
            logger.warning(f"⚠️ {missing} not found in the HTML.")
    if len(missing_sections) == 0:
        logger.info(f"🚀 QC report successfully updated all elements and saved to: {output_html_path}")
    elif len(updated_sections) != 0:
        logger.info(f"🚀 QC report successfully updated and saved to: {output_html_path}")


